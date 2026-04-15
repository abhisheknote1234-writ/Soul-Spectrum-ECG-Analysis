import asyncio
import json
import os
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional

import neurokit2 as nk
import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from scipy import signal
from scipy.stats import entropy as scipy_entropy

WINDOW_SECONDS = 30
STEP_SECONDS = 5
DEFAULT_FS = 256
SMOOTHING_POINTS = 5
legacy_powerline_env = os.getenv("ARC_POWERLINE_HZ")
POWERLINE_FREQ_HZ = float(os.getenv("ARC_POWERLINE_FREQ_HZ", legacy_powerline_env if legacy_powerline_env else "50"))
NOTCH_Q = float(os.getenv("ARC_NOTCH_Q", "30"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ARC_ALLOWED_ORIGINS", "*").split(",") if o.strip()]
MIN_ENTROPY_BINS = 6
MAX_ENTROPY_BINS = 12

# ARC scoring constants (empirically tuned defaults, intended for later calibration per cohort/device)
SD_RATIO_TARGET = 0.5
SD_RATIO_DECAY = 0.35
RR_VARIANCE_DECAY = 25000.0
ENTROPY_BASELINE = 1.5

AROUSAL_WEIGHTS = (0.40, 0.35, 0.25)     # HR, LFHF, LF
REGULATION_WEIGHTS = (0.45, 0.35, 0.20)  # RMSSD, HF, pNN50
COHERENCE_WEIGHTS = (0.45, 0.30, 0.25)   # SD ratio, entropy, variance


class BiosignalChunk(BaseModel):
    session_id: str = Field(default="default")
    sampling_rate: float = Field(default=DEFAULT_FS, gt=20)
    timestamp: Optional[float] = None
    ecg: List[float] = Field(default_factory=list)
    ppg: List[float] = Field(default_factory=list)
    emg: List[float] = Field(default_factory=list)


@dataclass
class SessionState:
    fs: float = DEFAULT_FS
    ecg: Deque[float] = field(default_factory=lambda: deque(maxlen=int(DEFAULT_FS * WINDOW_SECONDS * 2)))
    ppg: Deque[float] = field(default_factory=lambda: deque(maxlen=int(DEFAULT_FS * WINDOW_SECONDS * 2)))
    emg: Deque[float] = field(default_factory=lambda: deque(maxlen=int(DEFAULT_FS * WINDOW_SECONDS * 2)))
    result_history: Deque[Dict] = field(default_factory=lambda: deque(maxlen=SMOOTHING_POINTS))
    latest_result: Optional[Dict] = None
    total_samples: int = 0
    last_step_index: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def configure_buffers(self, fs: float):
        fs = float(fs)
        if fs <= 20:
            return
        if int(self.fs) == int(fs):
            return
        self.fs = fs
        maxlen = int(self.fs * WINDOW_SECONDS * 2)
        self.ecg = deque(self.ecg, maxlen=maxlen)
        self.ppg = deque(self.ppg, maxlen=maxlen)
        self.emg = deque(self.emg, maxlen=maxlen)


app = FastAPI(title="ARC Real-Time Biosignal API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, SessionState] = {}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def moving_average_smoothing(state: SessionState, payload: Dict) -> Dict:
    state.result_history.append(payload)
    h_keys = list(payload["features"].keys())

    smoothed = {
        "A": float(np.mean([d["A"] for d in state.result_history])),
        "R": float(np.mean([d["R"] for d in state.result_history])),
        "C": float(np.mean([d["C"] for d in state.result_history])),
        "state": payload["state"],
        "features": {k: float(np.mean([d["features"][k] for d in state.result_history])) for k in h_keys},
    }
    smoothed["state"] = map_state(smoothed["A"], smoothed["R"], smoothed["C"])
    return smoothed


def safe_array(data: Deque[float], samples: int) -> np.ndarray:
    if not data:
        return np.array([], dtype=float)
    arr = np.asarray(data, dtype=float)
    return arr[-samples:] if arr.size > samples else arr


def preprocess_signal(raw: np.ndarray, fs: float) -> np.ndarray:
    if raw.size < int(fs * 2):
        return raw.astype(float)

    x = raw.astype(float)
    x = signal.detrend(x, type="constant")

    low, high = 0.5 / (fs / 2), 40.0 / (fs / 2)
    high = min(high, 0.99)
    if 0 < low < high:
        b_band, a_band = signal.butter(4, [low, high], btype="bandpass")
        x = signal.filtfilt(b_band, a_band, x)

    notch_hz = POWERLINE_FREQ_HZ
    if fs / 2 > notch_hz:
        b_notch, a_notch = signal.iirnotch(notch_hz / (fs / 2), Q=NOTCH_Q)
        x = signal.filtfilt(b_notch, a_notch, x)

    k = int(fs * 0.75)
    if k % 2 == 0:
        k += 1
    k = max(3, min(k, x.size - 1 if x.size % 2 == 0 else x.size))
    if k > 3 and k % 2 == 1:
        baseline = signal.medfilt(x, kernel_size=k)
        x = x - baseline

    return x


def detect_rpeaks(ecg: np.ndarray, fs: float) -> np.ndarray:
    if ecg.size < int(fs * 3):
        return np.array([], dtype=int)
    try:
        cleaned = nk.ecg_clean(ecg, sampling_rate=fs, method="neurokit")
        _, rpeaks_info = nk.ecg_peaks(cleaned, sampling_rate=fs, method="neurokit")
        rpeaks = np.array(rpeaks_info.get("ECG_R_Peaks", []), dtype=int)
    except Exception as exc:
        print(f"[detect_rpeaks] neurokit2 fallback triggered: {exc}")
        prominence = max(np.std(ecg) * 0.35, 1e-6)
        distance = max(int(0.25 * fs), 1)
        rpeaks, _ = signal.find_peaks(ecg, distance=distance, prominence=prominence)
    return rpeaks


def rr_from_peaks(peaks: np.ndarray, fs: float) -> np.ndarray:
    if peaks.size < 2:
        return np.array([], dtype=float)
    rr = np.diff(peaks) / fs * 1000.0
    rr = rr[(rr > 300) & (rr < 2000)]
    return rr


def frequency_features(rr_ms: np.ndarray) -> Dict[str, float]:
    if rr_ms.size < 4:
        return {"LF": 0.0, "HF": 0.0, "LFHF": 0.0}

    rr_s = rr_ms / 1000.0
    t = np.cumsum(rr_s)
    t = t - t[0]
    if t[-1] <= 0:
        return {"LF": 0.0, "HF": 0.0, "LFHF": 0.0}

    fs_interp = 4.0
    t_i = np.arange(0, t[-1], 1 / fs_interp)
    if t_i.size < 16:
        return {"LF": 0.0, "HF": 0.0, "LFHF": 0.0}

    rr_interp = np.interp(t_i, t, rr_s)
    rr_interp = rr_interp - np.mean(rr_interp)

    freqs, psd = signal.welch(rr_interp, fs=fs_interp, nperseg=min(256, rr_interp.size))
    lf_mask = (freqs >= 0.04) & (freqs < 0.15)
    hf_mask = (freqs >= 0.15) & (freqs < 0.4)

    lf = float(np.trapezoid(psd[lf_mask], freqs[lf_mask])) if np.any(lf_mask) else 0.0
    hf = float(np.trapezoid(psd[hf_mask], freqs[hf_mask])) if np.any(hf_mask) else 0.0
    lfhf = float(lf / hf) if hf > 1e-10 else 0.0
    return {"LF": lf, "HF": hf, "LFHF": lfhf}


def nonlinear_features(rr_ms: np.ndarray) -> Dict[str, float]:
    if rr_ms.size < 2:
        return {"SD1": 0.0, "SD2": 0.0}
    diff_rr = np.diff(rr_ms)
    sd1 = float(np.sqrt(np.var(diff_rr, ddof=1) / 2.0)) if diff_rr.size > 1 else 0.0
    sdnn = float(np.std(rr_ms, ddof=1)) if rr_ms.size > 1 else 0.0
    sd2_sq = max(0.0, (2 * sdnn**2) - (sd1**2))
    sd2 = float(np.sqrt(sd2_sq))
    return {"SD1": sd1, "SD2": sd2}


def time_features(rr_ms: np.ndarray) -> Dict[str, float]:
    if rr_ms.size < 2:
        return {
            "HR": 0.0,
            "RMSSD": 0.0,
            "SDNN": 0.0,
            "pNN50": 0.0,
        }

    diff_rr = np.diff(rr_ms)
    hr = float(60000.0 / np.mean(rr_ms))
    rmssd = float(np.sqrt(np.mean(diff_rr**2)))
    sdnn = float(np.std(rr_ms, ddof=1))
    pnn50 = float(np.mean(np.abs(diff_rr) > 50.0) * 100.0)
    return {"HR": hr, "RMSSD": rmssd, "SDNN": sdnn, "pNN50": pnn50}


def map_state(a: float, r: float, c: float) -> str:
    if c > 0.75 and r > 0.65 and 0.35 <= a <= 0.75:
        return "BLUE"
    if a > 0.78 and r < 0.42:
        return "RED"
    if a > 0.62 and r >= 0.42:
        return "YELLOW"
    if r > 0.70 and c > 0.62:
        return "GREEN"
    if c > 0.85 and r > 0.75:
        return "WHITE"
    if r < 0.25 and a > 0.65:
        return "BLACK"
    return "GRAY"


def arc_from_features(features: Dict[str, float], rr_ms: np.ndarray) -> Dict[str, float]:
    hr = features["HR"]
    rmssd = features["RMSSD"]
    pnn50 = features["pNN50"]
    lf = features["LF"]
    hf = features["HF"]
    lfhf = features["LFHF"]
    sd1 = features["SD1"]
    sd2 = features["SD2"]

    norm_hr = clamp((hr - 55.0) / 45.0, 0.0, 1.0)
    norm_lfhf = clamp(lfhf / 4.0, 0.0, 1.0)
    norm_lf = clamp(lf / 0.25, 0.0, 1.0)

    norm_rmssd = clamp(rmssd / 80.0, 0.0, 1.0)
    norm_hf = clamp(hf / 0.20, 0.0, 1.0)
    norm_pnn50 = clamp(pnn50 / 60.0, 0.0, 1.0)

    sd_ratio = (sd1 / sd2) if sd2 > 1e-9 else 0.0
    sd_ratio_score = float(np.exp(-abs(sd_ratio - SD_RATIO_TARGET) / SD_RATIO_DECAY))

    rr_var = float(np.var(rr_ms)) if rr_ms.size > 1 else 0.0
    var_score = float(np.exp(-rr_var / RR_VARIANCE_DECAY))

    if rr_ms.size > 5:
        hist, _ = np.histogram(
            rr_ms,
            bins=min(MAX_ENTROPY_BINS, max(MIN_ENTROPY_BINS, int(np.sqrt(rr_ms.size)))),
            density=True,
        )
        hist = hist[hist > 0]
        rr_entropy = float(scipy_entropy(hist)) if hist.size else 0.0
    else:
        rr_entropy = 0.0
    entropy_score = float(np.exp(-max(rr_entropy - ENTROPY_BASELINE, 0.0)))

    aw_hr, aw_lfhf, aw_lf = AROUSAL_WEIGHTS
    rw_rmssd, rw_hf, rw_pnn50 = REGULATION_WEIGHTS
    cw_ratio, cw_entropy, cw_var = COHERENCE_WEIGHTS

    arousal = float(aw_hr * norm_hr + aw_lfhf * norm_lfhf + aw_lf * norm_lf)
    regulation = float(rw_rmssd * norm_rmssd + rw_hf * norm_hf + rw_pnn50 * norm_pnn50)
    coherence = float(cw_ratio * sd_ratio_score + cw_entropy * entropy_score + cw_var * var_score)

    return {
        "A": clamp(arousal, 0.0, 1.0),
        "R": clamp(regulation, 0.0, 1.0),
        "C": clamp(coherence, 0.0, 1.0),
    }


def compute_output(state: SessionState) -> Optional[Dict]:
    fs = state.fs
    n_window = int(fs * WINDOW_SECONDS)

    ecg = safe_array(state.ecg, n_window)
    ppg = safe_array(state.ppg, n_window)

    source = ecg if ecg.size >= int(fs * 3) else ppg
    if source.size < int(fs * 3):
        return None

    cleaned = preprocess_signal(source, fs)
    peaks = detect_rpeaks(cleaned, fs)
    rr_ms = rr_from_peaks(peaks, fs)
    if rr_ms.size < 3:
        return None

    features = {}
    features.update(time_features(rr_ms))
    features.update(frequency_features(rr_ms))
    features.update(nonlinear_features(rr_ms))

    arc = arc_from_features(features, rr_ms)
    state_label = map_state(arc["A"], arc["R"], arc["C"])

    payload = {
        "A": arc["A"],
        "R": arc["R"],
        "C": arc["C"],
        "state": state_label,
        "features": {
            "HR": features["HR"],
            "RMSSD": features["RMSSD"],
            "SDNN": features["SDNN"],
            "pNN50": features["pNN50"],
            "LF": features["LF"],
            "HF": features["HF"],
            "LFHF": features["LFHF"],
            "SD1": features["SD1"],
            "SD2": features["SD2"],
        },
    }
    return moving_average_smoothing(state, payload)


def get_session(session_id: str) -> SessionState:
    if session_id not in sessions:
        sessions[session_id] = SessionState()
    return sessions[session_id]


def ingest_chunk(chunk: BiosignalChunk) -> Optional[Dict]:
    state = get_session(chunk.session_id)
    with state.lock:
        state.configure_buffers(chunk.sampling_rate)

        if chunk.ecg:
            state.ecg.extend(float(x) for x in chunk.ecg)

        if chunk.ppg:
            state.ppg.extend(float(x) for x in chunk.ppg)

        if chunk.emg:
            state.emg.extend(float(x) for x in chunk.emg)

        batch_samples = max(len(chunk.ecg), len(chunk.ppg), len(chunk.emg), 0)
        state.total_samples += batch_samples

        step = int(state.fs * STEP_SECONDS)
        min_samples = int(state.fs * WINDOW_SECONDS)
        if state.total_samples < min_samples:
            return None

        if state.total_samples - state.last_step_index < step:
            return state.latest_result

        computed = compute_output(state)
        if computed is not None:
            state.latest_result = computed
            state.last_step_index = state.total_samples
        return state.latest_result


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/ingest-data")
def api_ingest_data(chunk: BiosignalChunk) -> Dict:
    result = ingest_chunk(chunk)
    return {
        "status": "ok",
        "ready": result is not None,
        "window_seconds": WINDOW_SECONDS,
        "step_seconds": STEP_SECONDS,
        "result": result,
    }


@app.get("/api/process-data")
def api_process_data(session_id: str = "default") -> Dict:
    state = get_session(session_id)
    with state.lock:
        if state.latest_result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No processed window yet. Stream at least {WINDOW_SECONDS}s of data first.",
            )
        return state.latest_result


@app.websocket("/ws/process-data")
async def ws_process_data(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                obj = json.loads(raw)
                chunk = BiosignalChunk(**obj)
            except Exception as exc:
                await websocket.send_json({"status": "error", "message": f"Invalid payload format: {str(exc)[:160]}"})
                continue

            result = ingest_chunk(chunk)
            if result is None:
                await websocket.send_json(
                    {
                        "status": "waiting",
                        "message": "Need 30s window before first inference",
                        "window_seconds": WINDOW_SECONDS,
                        "step_seconds": STEP_SECONDS,
                    }
                )
            else:
                await websocket.send_json(result)
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        return
