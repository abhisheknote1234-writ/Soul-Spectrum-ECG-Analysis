# ECG–HRV Orientation System

##  Overview

This project is a **real-time ECG + HRV monitoring system** that explores how physiological signals reflect **dynamic emotional and regulatory states**.

Unlike traditional HRV tools that only measure “high vs low HRV”, this system models HRV as a **continuous state transition process**.

It combines:

* Real-time ECG acquisition
* R-peak detection
* RR interval tracking
* HRV computation (RMSSD)
* State-based interpretation layer

---

##  Core Idea

Instead of asking:

> “Is HRV high or low?”

This project asks:

> **“What state of regulation is the system currently in?”**

---

##  System Pipeline

```text
ECG Signal → Preprocessing → R-Peak Detection → RR Intervals → HRV (RMSSD) → State Interpretation
```

---

##  Three Heart States (Model)

###  Instinct / Act (Low HRV)

* Contraction, protection, commitment
* Reduced variability
* Appears during strong emotional impact

---

###  Orient / Decide (Mid HRV)

* Evaluation, awareness, balance
* Stable HRV
* Represents decision-making phase

---

###  Adapt / Flow (High HRV)

* Openness, flexibility, synchronization
* High and smooth HRV
* Occurs during positive or flowing emotional states

---

##  Features

* Real-time ECG waveform visualization
* Robust R-peak detection
* RR interval tracking
* HRV computation (RMSSD)
* Live state classification
* Session recording and playback

---

##  Live Output

The system displays:

* ECG waveform
* BPM
* RR interval
* HRV (RMSSD)
* Current state:

  * INSTINCT
  * ORIENT
  * FLOW

---

##  Hardware Setup

* ECG sensor (AD8232 or similar)
* Arduino / ESP32
* Chest electrode placement
* Serial communication to PC

---

##  How to Run

```bash
pip install -r requirements.txt
python Ecg_Heartbeat.py
```

### Real-time API mode (A-R-C dashboard + HRV backend)

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- `arc_dashboard.html` in browser
- ensure frontend API base points to backend:
  - default: `http://localhost:8000`
  - optional in browser console: `localStorage.setItem("ARC_API_BASE", "http://localhost:8000")`
  - optional session selection: `localStorage.setItem("ARC_SESSION_ID", "default")`

### Data ingestion contract

- Stream raw samples (ECG/PPG/EMG) to backend:
  - `POST /api/ingest-data`
  - `WebSocket /ws/process-data`
- Read latest processed 30s window output every 5s:
  - `GET /api/process-data?session_id=default`

Returned payload:

```json
{
  "A": 0.62,
  "R": 0.55,
  "C": 0.71,
  "state": "YELLOW",
  "features": {
    "HR": 76.4,
    "RMSSD": 34.2,
    "SDNN": 52.8,
    "pNN50": 18.2,
    "LF": 0.11,
    "HF": 0.06,
    "LFHF": 1.83,
    "SD1": 24.6,
    "SD2": 58.7
  }
}
```

---

##  Experimental Insight

This system was tested using music as an emotional stimulus.

### Example Observations:

* Emotional intensity → HRV decrease → Instinct state
* Positive flow → HRV increase → Adapt state
* Neutral phase → Stable HRV → Orientation state

---

##  Limitations

* Not a medical diagnostic tool
* Sensitive to noise and electrode placement
* HRV influenced by multiple factors (activity, breathing, etc.)

---

##  Future Work

* Multi-sensor fusion (PPG, respiration)
* Real-time wearable integration
* Emotion-pattern modeling
* Color-based visualization system

---

##  Key Insight

> HRV is not just variability.
> It reflects **how the system adapts, decides, and responds over time.**

---

##  Note

This project is exploratory and focuses on bridging:

* physiology
* emotion
* behavioral patterns

---

##  Author

Abhishek Gupta
