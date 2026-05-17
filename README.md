

> ⚙️ **Note:** The underlying anomaly evaluation engines and LLM pipeline are completely decoupled from the test app layout. The analyzer will automatically recalibrate and re-learn normal operations against any application during its first 30 seconds of clean execution traffic.

---

## 🎓 Academic Context
This framework maps directly to the following instructional modules:
* **Chapter 13:** Observability — Signal collection methodology, modular log parsing, and time-series buffers.
* **Chapter 14:** Anomaly Detection — Feature-based risk scoring, rule evaluation paradigms, and dynamic baseline initialization.
* **Lab 3:** Dynamic Application Analysis without Host Instrumentation.
* **Lab 13:** Runtime Behavioral Profiling Architectures.

---

## 🛠️ Built With

* [Flask](https://flask.palletsprojects.com/) — Python web micro-framework
* [Chart.js](https://www.chartjs.org/) — Real-time telemetry visualization components
* [Ollama](https://ollama.com/) — Local LLM compilation runtime
* [phi3](https://azure.microsoft.com/en-us/blog/introducing-phi-3-redefining-what-is-possible-with-slms/) — Microsoft's 3.8B lightweight language model
* [ADB](https://developer.android.com/tools/adb) — Android Debug Bridge command line communications utilities
* [MITRE ATT&CK](https://attack.mitre.org/) — Globally-accessible knowledge base of adversary tactics and techniques

***

**AndroidBehaviorAnalysis v1.0** — *Academic Research Project# AndroidBehaviorAnalysis

### Android Runtime Intelligence Platform
*Dynamic behavioral profiling and AI-powered anomaly detection for Android applications. No root required.*

---

## 📋 Overview

**AndroidBehaviorAnalysis** is a runtime audit tool for Android applications. It connects to a running Android device or emulator via ADB, collects behavioral signals in real time, scores anomalies using a weighted feature model mapped to MITRE ATT&CK, and generates AI-powered root cause hypotheses using a local LLM—all without modifying the target app or requiring root access.

It produces structured audit reports comparable to tools like MobSF, Frida, and Drozer, with an added layer of AI-generated SOC-style diagnosis.

---

## 🏗️ Architecture
```text
Android Device / Emulator
          ↕  ADB (Android Debug Bridge)
    Python Backend
          ←→  Ollama (Local LLM · phi3)
          ↕  HTTP (Flask · localhost:5000)
  Web Dashboard (Browser · profiler/static/index.html)

```

---

## 📂 Project Structure

```text
AndroidBehaviorAnalysis/
├── app/                          ← Android test app (Android Studio)
│   └── src/main/java/com/audit/behaviortestapp/
│       └── MainActivity.java     ← 5 anomaly scenarios
├── profiler/                     ← Python backend + web dashboard
│   ├── main.py                   ← Entry point
│   ├── api.py                    ← Flask REST API + Ollama AI endpoint
│   ├── collector.py              ← ADB logcat reader + signal sampling
│   ├── detector.py               ← Anomaly scoring + MITRE ATT&CK mapping
│   └── static/
│       └── index.html            ← SOC-style live dashboard
└── README.md

```

---

## 🚀 Features

### 🔍 Signal Collection

* **Real-time Monitoring:** Reads ADB logcat dynamically from a connected device or emulator.
* **Granular Telemetry:** Samples 6 key signals every second: request rate, error rate, latency, crash count, retry count, and storage operations.
* **Hybrid Parser:** Combines JSON and regex log parsing to efficiently handle both structured and unstructured log lines.
* **IOC Extraction:** Endpoint paths are automatically captured directly from runtime log messages.

### 🛡️ Anomaly Detection

* **Baseline Learning:** Learns standard behavior automatically from the first 30 seconds of calm traffic.
* **Risk Scoring:** Uses a weighted feature deviation scoring system to output a dynamic 0 to 100 risk score.
* **Threat Mapping:** Uses 6 built-in detection rules mapped directly to MITRE ATT&CK matrices with specific confidence levels.
* **Lifecycle Management:** Automatically handles incidents (Open, Active, Closed) using a 45-second inactivity gap.
* **SOC Triage Workflow:** Allows operators to flag incidents as *Acknowledge*, *Mitigated*, or *False Positive*.

### 🧠 AI Analysis

* **100% Local Privacy:** Powered by `phi3` running via Ollama; no data ever leaves your machine.
* **Context-Aware Prompts:** Feeds active incidents, MITRE contexts, IOCs, and live signals into the local model.
* **Actionable Outputs:** Generates detailed root cause hypotheses, MITRE alignment, IOC analysis, and remediation steps.
* **Hardware Optimized:** Tested on NVIDIA RTX 4050 with CUDA support, delivering responses in under 30 seconds.

### 📊 SOC Dashboard

* **Live Telemetry Charts:** Real-time visual monitoring of request rates, error rates, latency, crashes, and retries.
* **Threat Gauge:** 10-segment threat level bar indicating real-time severity.
* **Incident Timeline:** Expandable analytical drawers revealing captured telemetry and IOCs at the exact moment of trigger.
* **Kill Chain View:** Dedicated panel for alerts and quick triage action items.
* **Signal Feed:** Live deviation tables displaying a scrolling 60-second history chart.
* **Reporting:** One-click export for comprehensive HTML audit reports.

---

## 📋 Detection Rules

| Rule | Severity | MITRE Mapping | Confidence |
| --- | --- | --- | --- |
| **Data Exfiltration Pattern** | 🔴 Critical | `T1048` | High |
| **Silent Application Hang** | 🟠 High | `T1499` | Medium |
| **Infinite Retry Loop** | 🟠 High | `T1071.001` | Low |
| **Request Spam** | 🟠 High | `T1498` | Low |
| **Crash Storm** | 🟠 High | `T1499.004` | Low |
| **Timeout / Slow Response** | 🟡 Medium | `T1499` | Low |

---

## 🔄 Comparison with Existing Tools

| Tool | Core Methodology | AndroidBehaviorAnalysis Advantage |
| --- | --- | --- |
| **MobSF** | Static & Dynamic Analysis, API security testing | Adds context-aware, AI-driven root cause diagnosis. |
| **Frida** | Runtime instrumentation and hooking | Works **rootless** via native ADB, eliminating jailbreak setups. |
| **Drozer** | Attack surface enumeration and exploitation | Introduces continuous behavioral anomaly scoring mapped to MITRE. |
| **Manual Logcat** | Raw terminal log streams without automation | Automates analysis with scoring, lifecycle management, and explanations. |

---

## ⚙️ Requirements

### System Requirements

* **OS:** Windows 10 or 11 (fully tested), macOS, or Linux
* **Python:** v3.10 or later
* **Android Tools:** Android Studio (for integrated ADB) or standalone `platform-tools`
* **LLM Engine:** Ollama with the `phi3` model pulled

### Hardware (Recommended for Local Inference)

* Dedicated NVIDIA GPU with CUDA support
* *Tested Configuration:* Intel Core i9-13900H with NVIDIA RTX 4050 Laptop GPU
* **RAM:** 16 GB minimum recommended

### Python Dependencies

```text
flask
flask-cors
colorama
requests

```

---

## 🛠️ Installation & Setup

### Step 1: Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/AndroidBehaviorAnalysis.git](https://github.com/YOUR_USERNAME/AndroidBehaviorAnalysis.git)
cd AndroidBehaviorAnalysis

```

### Step 2: Configure Python Virtual Environment

```bash
cd profiler
python -m venv venv

```

* **Windows:**
```cmd
venv\Scripts\activate

```


* **macOS / Linux:**
```bash
source venv/bin/activate

```



Install required modules:

```bash
pip install flask flask-cors colorama requests

```

### Step 3: Set Up Ollama & Local Model

Download and install Ollama from [ollama.com/download](https://ollama.com/download).

Pull the required model:

```bash
ollama pull phi3

```

*(Optional)* Enable GPU acceleration on Windows before starting the server:

```cmd
set OLLAMA_NUM_GPU=999
ollama serve

```

### Step 4: Map Your Android Device

1. Ensure your device/emulator has USB Debugging enabled.
2. Run `adb devices` to fetch your unique string identifier (e.g., `emulator-5556`).
3. Open `profiler/collector.py` and modify the device mapping configuration:
```python
DEVICE_ID = "emulator-5556"

```



### Step 5: Run the Profiler

```bash
python main.py

```

Open `profiler/static/index.html` directly in your preferred web browser to access the SOC Dashboard.

---

## 📱 Android Test App

The `app/` directory contains **BehaviorTestApp**, an intentionally buggy Android application preconfigured with 5 distinct anomaly simulation scenarios:

* **Normal Request:** Dispatches one standard GET request every 3 seconds. Use this scenario to train your 30-second quiet baseline.
* **Retry Loop:** Continuously calls an endpoint returning a `401 Unauthorized` response, retrying immediately without backoff.
* **Request Spam:** Allocates 6 parallel threads firing rapid network requests simultaneously without internal throttling limits.
* **Crash Storm:** Intentionally throws a `NullPointerException` every 500ms, creating dense application crash dumps.
* **Slow / Timeout:** Contacts a target endpoint with a forced 10-second server-side delay, exceeding the app's default 5-second client timeout threshold.

> 💡 **Usage:** Open the `app/` workspace in Android Studio, deploy it onto your connected target device, run the scenarios, and observe the mutations on your dashboard feed.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/status` | Returns server health, active tracking metadata, and baseline statuses. |
| `GET` | `/api/signals/current` | Returns the latest 1-second sampled signal snapshot. |
| `GET` | `/api/signals/history` | Fetches a rolling collection of telemetry snapshots from the last 60 seconds. |
| `GET` | `/api/logs` | Returns the 50 most recent raw logcat lines processed by the backend. |
| `GET` | `/api/incidents` | Fetches all detected structural incidents generated during the active session. |
| `GET` | `/api/anomalies` | Functional alias route mapping directly to `/api/incidents`. |
| `POST` | `/api/incidents/:id/triage` | Mutates triage status state (`acknowledged`, `mitigated`, `false_positive`). |
| `POST` | `/api/analyze` | Forces an on-demand AI triage root cause generation cycle via local Ollama execution. |

---

## 🎯 Targeting a Custom Application

To monitor a third-party application instead of the bundled test app, open `profiler/collector.py` and adjust the target variables:

```python
PACKAGE = "com.your.target.app"
DEVICE_ID = "your-device-id"

```

> ⚙️ **Note:** The underlying anomaly evaluation engines and LLM pipeline are completely decoupled from the test app layout. The analyzer will automatically recalibrate and re-learn normal operations against any application during its first 30 seconds of clean execution traffic.

---

## 🎓 Academic Context

This framework maps directly to the following instructional modules:

* **Chapter 13:** Observability — Signal collection methodology, modular log parsing, and time-series buffers.
* **Chapter 14:** Anomaly Detection — Feature-based risk scoring, rule evaluation paradigms, and dynamic baseline initialization.
* **Lab 3:** Dynamic Application Analysis without Host Instrumentation.
* **Lab 13:** Runtime Behavioral Profiling Architectures.

---

## 🛠️ Built With

* [Flask](https://flask.palletsprojects.com/) — Python web micro-framework
* [Chart.js](https://www.chartjs.org/) — Real-time telemetry visualization components
* [Ollama](https://ollama.com/) — Local LLM compilation runtime
* [phi3](https://www.google.com/search?q=https://azure.microsoft.com/en-us/blog/introducing-phi-3-redefining-what-is-possible-with-slms/) — Microsoft's 3.8B lightweight language model
* [ADB]() — Android Debug Bridge command line communications utilities
* [MITRE ATT&CK]() — Globally-accessible knowledge base of adversary tactics and techniques

---

**AndroidBehaviorAnalysis v1.0** — *Academic Research Project*

```

```
