# ECG–HRV Orientation Project

## Overview

This project is a **live ECG & HRV monitoring system** built to explore how the human heart **adapts, orients, decides, and acts** over time — especially under **emotional and musical stimuli**.

Rather than treating HRV as just a fitness number, this project treats HRV as a **dynamic language of regulation**.

I built:

* A **real-time ECG live monitor**
* Beat detection (R-peaks)
* RR interval tracking
* Short-window HRV (RMSSD)
* A **state-based interpretation layer** that maps HRV shifts into:

  * **Instinct / Act**
  * **Orient / Decide**
  * **Adapt / Flow**

This README explains **what those states mean** and **how my HRV shifted while listening to two songs**, showing how emotion, meaning, and rhythm directly shape heart regulation.

---

## Why this project exists

Most HRV tools answer only one question:

> “Is HRV high or low?”

This project asks a deeper one:

> **“What phase of regulation is my heart in right now?”**

Because real human experience is not binary — it moves through phases.

---

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

---

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

---

### Adapt / Flow (High HRV)

**State:** Expansion, openness, emotional flow

* HRV is higher and smooth
* Nervous system is flexible
* Heart synchronizes with rhythm and meaning

This appears when:

* Music feels hopeful
* Lyrics resonate positively
* Emotion moves freely without resistance

---

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

This turns raw physiology into **interpretable experience**. fileciteturn0file0

---

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

---

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
