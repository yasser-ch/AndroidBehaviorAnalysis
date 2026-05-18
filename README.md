# AndroidBehaviorAnalysis

<div align="center">

### Android Runtime Intelligence Platform

*Dynamic behavioral profiling and AI-powered anomaly detection for Android applications. No root required.*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Android](https://img.shields.io/badge/Android-API%2037-3DDC84?style=flat-square&logo=android&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)
![MITRE ATT&CK](https://img.shields.io/badge/MITRE-ATT%26CK-FF0000?style=flat-square)
![License](https://img.shields.io/badge/License-Academic-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

</div>

---

## Demo

https://github.com/user-attachments/assets/00be01ce-6dfb-43b6-b3f1-19c69b3215dc

---

## Overview

**AndroidBehaviorAnalysis** is a runtime audit tool for Android applications. It connects to a running Android device or emulator via ADB, collects behavioral signals in real time, scores anomalies using a weighted feature model mapped to MITRE ATT&CK, and generates AI-powered root cause hypotheses using a local LLM — all without modifying the target app or requiring root access.

It produces structured audit reports comparable to tools like MobSF, Frida, and Drozer, with an added layer of AI-generated SOC-style diagnosis.

> **Academic Project** — École Nationale des Sciences Appliquées de Marrakech (ENSAM)  
> Module: *Programmation et Sécurité des Applications Mobiles Android*  
> Supervisor: Prof. Mohamed LACHGAR

---

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Detection Rules](#detection-rules)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation & Setup](#installation--setup)
- [Android Test App](#android-test-app)
- [API Reference](#api-reference)
- [Comparison with Existing Tools](#comparison-with-existing-tools)
- [Academic Context](#academic-context)
- [Built With](#built-with)
- [Team](#team)

---

## Architecture

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

---

## Features

### 🔍 Signal Collection
| Signal | Description |
|--------|-------------|
| Request Rate | HTTP requests per minute sampled via logcat |
| Error Rate | Percentage of failed requests per sampling window |
| Avg Latency | Round-trip time in milliseconds per request |
| Crash Count | NullPointerException and fatal signals per second |
| Retry Count | Repeated network attempt frequency |
| Storage Ops | File read/write events on internal storage |

- **Real-time monitoring** — reads ADB logcat dynamically, no polling delay
- **Hybrid parser** — combines JSON structured logs and regex for unstructured lines
- **IOC extraction** — endpoint paths captured automatically from runtime log messages
- **Baseline learning** — learns normal behavior from the first 30 seconds of calm traffic

### ⚡ Anomaly Detection

- **Weighted z-score scoring** — outputs a dynamic 0–100 risk score per signal window
- **6 detection rules** mapped to MITRE ATT&CK with confidence levels
- **Lifecycle management** — incidents transition Open → Active → Closed after 45s inactivity
- **SOC triage workflow** — operators can flag Acknowledged / Mitigated / False Positive

### 🤖 AI Analysis

- **100% local inference** — powered by phi3 via Ollama, no data ever leaves the machine
- **Context-aware prompts** — feeds active incidents, MITRE IDs, IOCs, and live signals to the model
- **Actionable outputs** — root cause hypotheses, MITRE alignment, IOC analysis, remediation steps
- **Hardware optimized** — tested on NVIDIA RTX 4050 with CUDA, responses under 30 seconds

### 📊 SOC Dashboard

- Live telemetry charts (request rate, error rate, latency, crashes, retries)
- 10-segment threat gauge with real-time severity indicator
- Incident timeline with expandable drawers showing telemetry at trigger moment
- Kill Chain view with quick triage actions
- Signal Feed with 60-second scrolling history
- One-click HTML audit report export

---

## Detection Rules

| Rule | Severity | MITRE ID | Tactic | Confidence |
|------|----------|----------|--------|------------|
| Data Exfiltration Pattern | 🔴 Critical | T1048 | Exfiltration | High |
| Silent Application Hang | 🟠 High | T1499 | Impact | Medium |
| Infinite Retry Loop | 🟠 High | T1071.001 | C2 | Low |
| Request Spam | 🟠 High | T1498 | Impact | Low |
| Crash Storm | 🟠 High | T1499.004 | Impact | Low |
| Timeout / Slow Response | 🟡 Medium | T1499 | Impact | Low |

---

## Project Structure

```
AndroidBehaviorAnalysis/
│
├── app/                              # Android Studio test application
│   └── src/main/java/com/audit/
│       behaviortestapp/
│           └── MainActivity.java     # 5 anomaly simulation scenarios
│
├── profiler/                         # Python backend + dashboard
│   ├── main.py                       # Entry point — starts server + checklist
│   ├── api.py                        # Flask REST API + Ollama orchestration
│   ├── collector.py                  # ADB logcat reader + signal sampler
│   ├── detector.py                   # Anomaly scoring + MITRE ATT&CK mapping
│   └── static/
│       └── index.html                # SOC-style live web dashboard
│
└── README.md
```

---

## Requirements

### System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 (fully tested), macOS, Linux |
| Python | 3.10 or later |
| Android Tools | Android Studio or standalone platform-tools |
| LLM Engine | Ollama with phi3 model pulled |

### Recommended Hardware for Local Inference

- Dedicated NVIDIA GPU with CUDA support
- Tested: Intel Core i9-13900H + NVIDIA RTX 4050 Laptop GPU
- 16 GB RAM minimum

### Python Dependencies

```
flask
flask-cors
colorama
requests
```

---

## Installation & Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Abdeljalil-Fajri/AndroidBehaviorAnalysis.git
cd AndroidBehaviorAnalysis
```

### Step 2 — Configure Python Environment

```bash
cd profiler
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install flask flask-cors colorama requests
```

### Step 3 — Set Up Ollama & Local Model

```bash
# Download Ollama from https://ollama.com and then:
ollama pull phi3

# Optional: enable GPU acceleration (Windows)
set OLLAMA_NUM_GPU=999
ollama serve
```

### Step 4 — Map Your Android Device

```bash
adb devices
# Example output: emulator-5556   device
```

Open `collector.py` and set your device ID:

```python
DEVICE_ID = "emulator-5556"   # match your adb devices output
```

### Step 5 — Run the Profiler

```bash
python main.py
```

Open `profiler/static/index.html` in your browser to access the live SOC Dashboard.

---

## Android Test App

The `app/` folder contains **BehaviorTestApp** — an intentionally instrumented Android application with 5 anomaly simulation scenarios:

| Button | Behavior | Expected Detection |
|--------|----------|--------------------|
| Normal Request | 1 GET every 3s to httpbin.org | No alert — used to train baseline |
| Retry Loop | Continuous retry on 401 without backoff | `INFINITE_RETRY` — T1071.001 |
| Request Spam | 6 parallel threads, no throttle | `REQUEST_SPAM` — T1498 |
| Crash Storm | NullPointerException every 500ms | `CRASH_STORM` — T1499.004 |
| Slow / Timeout | 10s server delay vs 5s client timeout | `TIMEOUT_PATTERN` — T1499 |

> **Tip:** Always start with **Normal Request** for 30+ seconds to let the baseline calibrate before triggering anomaly scenarios.

---

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

### Example Response — `/api/signals/current`

```json
{
  "request_rate": 4560,
  "error_rate": 100.0,
  "avg_latency": 0,
  "crash_count": 0,
  "retry_count": 0,
  "storage_ops": 0,
  "anomaly_score": 40,
  "timestamp": "2026-05-18T15:10:00"
}
```

---

## Targeting a Custom Application

To monitor any third-party app instead of the bundled test app, edit `collector.py`:

```python
PACKAGE   = "com.your.target.app"
DEVICE_ID = "your-device-id"
```

The anomaly engine and LLM pipeline are fully decoupled from the test app. The system auto-recalibrates its baseline against any application during the first 30 seconds of clean traffic.

---

## Comparison with Existing Tools

| Tool | Core Methodology | AndroidBehaviorAnalysis Advantage |
|------|-----------------|----------------------------------|
| **MobSF** | Static + dynamic analysis, API security testing | Adds context-aware AI-driven root cause diagnosis |
| **Frida** | Runtime instrumentation and hooking | Works rootless via ADB — no jailbreak setup required |
| **Drozer** | Attack surface enumeration and exploitation | Adds continuous behavioral scoring mapped to MITRE |
| **Manual Logcat** | Raw terminal log streams | Automates scoring, lifecycle management, and AI explanation |

---

## Academic Context

This framework maps to the following course modules:

| Module | Topic |
|--------|-------|
| Chapter 13 | Observability — signal collection, log parsing, time-series buffers |
| Chapter 14 | Anomaly Detection — feature scoring, rule evaluation, baseline init |
| Lab 3 | Dynamic analysis without host instrumentation |
| Lab 13 | Runtime behavioral profiling architectures |

---

## Built With

| Technology | Role |
|------------|------|
| [Flask](https://flask.palletsprojects.com/) | Python web micro-framework |
| [Chart.js](https://www.chartjs.org/) | Real-time telemetry visualization |
| [Ollama](https://ollama.com/) | Local LLM runtime |
| [phi3](https://ollama.com/library/phi3) | Microsoft 3.8B language model |
| [ADB](https://developer.android.com/tools/adb) | Android Debug Bridge |
| [MITRE ATT&CK](https://attack.mitre.org/matrices/mobile/) | Adversary tactics and techniques knowledge base |

---

## Team

| Name | Role |
|------|------|
| Zakaria Aouianti | Android App Development |
| Yasser Chettour | Anomaly Detection Engine |
| Abdeljalil Fajri | Backend API & Infrastructure |
| Mohammed Ait Ourajli | Dashboard & AI Integration |

> École Nationale des Sciences Appliquées de Marrakech — 2025/2026

---

<div align="center">

**AndroidBehaviorAnalysis v1.0** — *Academic Research Project*

</div>
