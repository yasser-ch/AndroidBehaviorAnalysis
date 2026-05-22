# AndroidBehaviorAnalysis — Runtime Intelligence Platform for Android

![AndroidBehaviorAnalysis Banner](https://img.shields.io/badge/AndroidBehaviorAnalysis-v1.0-3DDC84?style=for-the-badge&logo=android&logoColor=white)

This platform enables real-time behavioral profiling and AI-powered anomaly detection for Android applications. It connects to a running Android device or emulator via ADB, collects behavioral signals, scores anomalies using a weighted feature model mapped to **MITRE ATT&CK**, and generates AI-powered root cause hypotheses using a local LLM — all without modifying the target app or requiring root access.

## Table of Contents

- [Software Architecture](#software-architecture)
- [Features](#features)
- [Detection Rules](#detection-rules)
- [Frontend](#frontend)
- [Backend](#backend)
- [Getting Started](#getting-started)
- [Android Test App](#android-test-app)
- [API Reference](#api-reference)
- [Video Demonstration](#video-demonstration)
- [Contributing](#contributing)

## Software Architecture

```
┌─────────────────────────────────┐
│   Android Device / Emulator     │
│   BehaviorTestApp (5 scenarios) │
└──────────────┬──────────────────┘
               │ ADB (Android Debug Bridge)
               ▼
┌─────────────────────────────────┐
│        Python Backend           │
│  collector.py → detector.py     │
│       api.py (Flask :5000)      │
└──────────┬──────────────────────┘
           │  Local Inference
           ▼
┌─────────────────────────────────┐
│   Ollama — phi3 (3.8B)          │
│   100% local, no data leak      │
└──────────┬──────────────────────┘
           │  HTTP
           ▼
┌─────────────────────────────────┐
│     SOC Web Dashboard           │
│  profiler/static/index.html     │
└─────────────────────────────────┘
```

The application architecture uses a **Python/Flask** backend for signal collection, anomaly detection, and LLM orchestration, with a static **HTML/JS** SOC dashboard as the frontend. Communication with the Android device is done via **ADB (Android Debug Bridge)**.

## Features

### Signal Collection
| Signal | Description |
|--------|-------------|
| Request Rate | HTTP requests per minute sampled via logcat |
| Error Rate | Percentage of failed requests per sampling window |
| Avg Latency | Round-trip time in milliseconds per request |
| Crash Count | NullPointerException and fatal signals per second |
| Retry Count | Repeated network attempt frequency |
| Storage Ops | File read/write events on internal storage |

### Anomaly Detection
- Weighted z-score scoring with a dynamic 0–100 risk score per signal window
- 6 detection rules mapped to MITRE ATT&CK with confidence levels
- Lifecycle management: incidents transition Open → Active → Closed after 45s inactivity
- SOC triage workflow: operators can flag Acknowledged / Mitigated / False Positive

### AI Analysis
- 100% local inference powered by **phi3** via Ollama — no data leaves the machine
- Context-aware prompts feeding active incidents, MITRE IDs, IOCs, and live signals
- Actionable outputs: root cause hypotheses, MITRE alignment, IOC analysis, remediation steps

## Detection Rules

| Rule | Severity | MITRE ID | Tactic | Confidence |
|------|----------|----------|--------|------------|
| Data Exfiltration Pattern | 🔴 Critical | T1048 | Exfiltration | High |
| Silent Application Hang | 🟠 High | T1499 | Impact | Medium |
| Infinite Retry Loop | 🟠 High | T1071.001 | C2 | Low |
| Request Spam | 🟠 High | T1498 | Impact | Low |
| Crash Storm | 🟠 High | T1499.004 | Impact | Low |
| Timeout / Slow Response | 🟡 Medium | T1499 | Impact | Low |

## Frontend

### Technologies Used

- HTML
- CSS
- JavaScript
- Chart.js

## Backend

### Technologies Used

- Python 3.10+
- Flask
- Ollama (phi3 — 3.8B local LLM)
- ADB (Android Debug Bridge)

## Backend Project Structure

The backend code follows a modular and organized structure, leveraging Flask for a lightweight and efficient API layer.

### 1. profiler/main.py

- *Entry Point:* Starts the Flask server and runs the setup checklist on launch.

### 2. profiler/api.py

- *Controller Layer:* Exposes all REST endpoints. Handles requests, coordinates between the collector, detector, and Ollama LLM orchestration.

### 3. profiler/collector.py

- *Signal Collector:* Reads ADB logcat in real time, parses structured and unstructured log lines, extracts IOCs, and maintains a rolling 60-second signal history.

### 4. profiler/detector.py

- *Anomaly Engine:* Applies weighted z-score scoring, evaluates detection rules, manages incident lifecycle, and maps findings to MITRE ATT&CK tactics.

### Dependencies

```
flask
flask-cors
colorama
requests
```

Install with:

```sh
pip install flask flask-cors colorama requests
```

## Getting Started

Here are step-by-step instructions to set up and run the project locally:

### Prerequisites

1. *Git:*
   - Make sure you have Git installed. If not, download and install it from [git-scm.com](https://git-scm.com/).

2. *Python 3.10+:*
   - Download from [python.org](https://www.python.org/downloads/).

3. *Android Debug Bridge (ADB):*
   - Install [Android Studio](https://developer.android.com/studio) or standalone [platform-tools](https://developer.android.com/tools/releases/platform-tools).
   - Enable **USB Debugging** on your Android device or start an emulator.

4. *Ollama:*
   - Download from [ollama.com](https://ollama.com) and pull the phi3 model:
     ```bash
     ollama pull phi3
     ```

### Backend Setup

1. *Clone the Project:*
   ```bash
   git clone https://github.com/Abdeljalil-Fajri/AndroidBehaviorAnalysis.git
   cd AndroidBehaviorAnalysis
   ```

2. *Configure Python Environment:*
   ```bash
   cd profiler
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate

   pip install flask flask-cors colorama requests
   ```

3. *Set Up Ollama:*
   ```bash
   # Optional: enable GPU acceleration (Windows)
   set OLLAMA_NUM_GPU=999
   ollama serve
   ```

4. *Map Your Android Device:*
   ```bash
   adb devices
   # Example output: emulator-5556   device
   ```

   Open `collector.py` and set your device ID:
   ```python
   DEVICE_ID = "emulator-5556"   # match your adb devices output
   ```

5. *Run the Profiler:*
   ```bash
   python main.py
   ```

   Open `profiler/static/index.html` in your browser to access the live SOC Dashboard.

### Android Test App Setup

1. Open the `app/` folder in **Android Studio**.
2. Build and deploy **BehaviorTestApp** to your device or emulator.
3. Always press **Normal Request** first for 30+ seconds to let the baseline calibrate before triggering anomaly scenarios.

## Android Test App

The `app/` folder contains **BehaviorTestApp** — an intentionally instrumented Android application with 5 anomaly simulation scenarios:

| Button | Behavior | Expected Detection |
|--------|----------|--------------------|
| Normal Request | 1 GET every 3s to httpbin.org | No alert — used to train baseline |
| Retry Loop | Continuous retry on 401 without backoff | `INFINITE_RETRY` — T1071.001 |
| Request Spam | 6 parallel threads, no throttle | `REQUEST_SPAM` — T1498 |
| Crash Storm | NullPointerException every 500ms | `CRASH_STORM` — T1499.004 |
| Slow / Timeout | 10s server delay vs 5s client timeout | `TIMEOUT_PATTERN` — T1499 |

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Server health, tracking metadata, baseline status |
| `GET` | `/api/signals/current` | Latest 1-second signal snapshot |
| `GET` | `/api/signals/history` | Rolling 60-second telemetry history |
| `GET` | `/api/logs` | Last 50 raw logcat lines |
| `GET` | `/api/incidents` | All detected incidents for the active session |
| `GET` | `/api/anomalies` | Alias for `/api/incidents` |
| `POST` | `/api/incidents/:id/triage` | Set status: `acknowledged`, `mitigated`, `false_positive` |
| `POST` | `/api/analyze` | Trigger on-demand AI root cause analysis via Ollama |

## Video Demonstration

https://github.com/user-attachments/assets/00be01ce-6dfb-43b6-b3f1-19c69b3215dc

## Contributing

We welcome contributions from everyone, and we appreciate your help to make this project even better! If you would like to contribute, please follow these guidelines:

## Contributors

- Zakaria Aouianti — Android App Development ([GitHub](https://github.com/Abdeljalil-Fajri/AndroidBehaviorAnalysis))
- Yasser Chettour — Anomaly Detection Engine ([GitHub](https://github.com/Abdeljalil-Fajri/AndroidBehaviorAnalysis))
- Abdeljalil Fajri — Backend API & Infrastructure ([GitHub](https://github.com/Abdeljalil-Fajri/AndroidBehaviorAnalysis))
- Mohammed Ait Ourajli — Dashboard & AI Integration ([GitHub](https://github.com/Abdeljalil-Fajri/AndroidBehaviorAnalysis))
- Mohamed Lachgar — Supervisor ([ResearchGate](https://www.researchgate.net/profile/Mohamed-Lachgar))

> École Nationale des Sciences Appliquées de Marrakech — 2025/2026
