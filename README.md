# ECG–HRV Orientation Project

## Overview

This project is a **live ECG & HRV monitoring system** built to explore how the human heart **adapts, orients, decides, and acts** over time — This project is just to give a overview how our body percive things under **emotional and musical stimuli**.

Rather than treating HRV as just a fitness number, this project treats HRV as a **dynamic language of regulation**.

Because real human experience is not binary, it moves through phases.
And the main part, what these phases actually meant. Do they have a deeper connection with our thoughts? Do they have connections with our actions? Our Body language? Behaviour?

To Find this, I built:

* A **real-time ECG live monitor**
* Beat detection (R-peaks)
* RR interval tracking
* Short-window HRV (RMSSD)
* A **state-based interpretation layer** that maps HRV shifts into:

  * **Instinct / Act**
  * **Orient / Decide**
  * **Adapt / Flow**

This README explains **what those states mean** and **how my HRV shifted while listening to two songs**, showing how emotion, meaning, and rhythm directly shape heart regulation.

**Why this project exists**

Most HRV tools answer only one question:
“Is HRV high or low?”

This project asks a deeper one:
**“What phase of regulation is my heart in right now?”**

## The Three Heart States (Core Model)

### Act / Instinct (Low HRV)
**State:** Action, protection, contraction

* HRV is low and tight
* System is conserving or bracing
* Little internal flexibility

This state appears when:

* Lyrics hit emotionally hard
* A memory is triggered
* The system commits to a feeling

This is **not bad** — it is **decisive**.

### Orient / Decide (Mid HRV)
**State:** Pause, evaluation, choice

* HRV is moderate and stable
* Signals from heart and brain are balanced
* Multiple directions are visible

This is the **thinking phase**:

* Not reacting
* Not flowing blindly
* But *choosing direction*

This is where awareness lives.

### Adapt / Flow (High HRV)
**State:** Expansion, openness, emotional flow

* HRV is higher and smooth
* Nervous system is flexible
* Heart synchronizes with rhythm and meaning

This appears when:

* Music feels hopeful
* Lyrics resonate positively
* Emotion moves freely without resistance

## Live ECG System (What I Built)
The system:

* Streams ECG data from a sensor (Arduino → Serial)
* Smooths the signal
* Detects R-peaks in real time
* Computes RR intervals
* Computes **short-window HRV (RMSSD)**
* Displays:

  * ECG waveform
  * BPM
  * RR interval (ms)
  * HRV value
  * **Current heart state label**

The state labels update live:

* **RIGID SYSTEM / INSTINCT**
* **ORIENTING / DECIDING**
* **ADAPTING / FLOWING**

This turns raw physiology into **interpretable experience**.

## How to Run This Project
### Hardware Setup

* ECG sensor connected to Arduino (e.g., AD8232 or equivalent)
* Correct electrode placement on the chest
* Arduino connected to laptop via USB

Upload the provided Arduino sketch using **Arduino IDE**.


### Software Setup

Make sure you have **Python 3.9+** installed.
Install all required dependencies:

```bash
pip install -r requirements.txt
```

---

### Run Live ECG Monitor

1. Open the Python file for the live ECG monitor
2. Set the correct serial port (e.g., `COM3` or `/dev/ttyUSB0`)
3. Run:

```bash
python Ecg_Heartbeat.py
```

You should see:

* Live ECG waveform
* BPM, RR interval, HRV values
* Real-time state classification

---

### Record a Session

* Press **`r`** to start recording
* Press **`r`** again to stop
* Data is saved automatically as a CSV file

### Analyze Recorded Data

Use the provided analysis scripts to:

* Plot RR Interval (HRV tachogram)
* Plot HRV (RMSSD) over time
* Visualize state transitions during music listening

### Notes

* This project is **exploratory**, not a medical diagnostic tool
* Results depend on electrode placement, noise, and emotional engagement
* Best results are obtained when the body is stil


## Emotional HRV Analysis Using Music
### Song 1: *Love Is Gone*

**What happened:**

* At the beginning of listening:

  * HRV rises
  * The system is **adapting** to sound, melody, visuals
  * Heart is open, receptive, exploratory

This is the **Orient → Adapt phase**.

* As lyrics progress and meaning becomes heavier:

  * HRV drops
  * RR intervals tighten
  * The system **contracts**

This marks a shift into **Act / Instinct**.

**Interpretation:**
The heart first *listens*.
Then it *understands*.
Then it *commits emotionally*.

The drop in HRV is not weakness — it is **emotional fixing**.
The heart takes a stance.

### Song 2: *Welcome to My World*
**What happened:**

* From early listening:

  * HRV rises smoothly
  * BPM increases with stability
  * The heart synchronizes with rhythm

* As lyrics flow with positivity:

  * HRV remains high and stable
  * No sharp contractions
  * Emotional expansion continues

**Interpretation:**
This song did not push the heart into defense.
It invited it into **hope and openness**.

The heart behaved as if:

> *“Something good is possible again.”*

This is **Adapt / Flow** sustained.

---

## Key Insight of This Project

HRV does **not** only measure stress.

It reveals:

* When the heart is **listening**
* When it is **deciding**
* When it is **acting**

Music became a **controlled emotional input**.
HRV became the **output language**.

This proves that:

> **Emotion is not random — it is regulated, phased, and measurable.**

---

## What This Project Is (and Is Not)

✔ Not a medical diagnostic tool
✔ Not just a BPM counter
✔ Not only about high vs low HRV

It *is*:

* A physiological + emotional interface
* A live nervous-system mirror
* A foundation for deeper heart–emotion research

---

## Future Directions

* Deeper state segmentation (micro-orientation)
* Mapping lyrics timestamps → HRV shifts
* Color-based HRV visualization
* Multi-sensor fusion (breathing, motion)

---

## Final Note

This project shows that the heart:

* Adapts before the mind understands
* Decides before words form
* Acts when meaning settles

**HRV is not just variability.**
It is **direction in motion**.
