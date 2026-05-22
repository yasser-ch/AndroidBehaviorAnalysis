<img width="182" height="150" alt="android_behavior_analysis_architecture" src="https://github.com/user-attachments/assets/577aec5f-dbc1-4563-93b2-9e2de39eee3d" /># AndroidBehaviorAnalysis — Runtime Intelligence Platform for Android

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

![Uploading a<svg width="100%" viewBox="0 0 680 560" role="img" style="" xmlns="http://www.w3.org/2000/svg">
<title style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">Architecture AndroidBehaviorAnalysis</title>
<desc style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">Diagramme structurel : Android Device → ADB → Python Backend (collector, detector, api) → Ollama phi3 LLM → SOC Web Dashboard</desc>
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
<mask id="imagine-text-gaps-vo2xp2" maskUnits="userSpaceOnUse"><rect x="0" y="0" width="680" height="560" fill="white"/><rect x="247.921875" y="47" width="184.391845703125" height="22" fill="black" rx="2"/><rect x="222.1796875" y="70.5" width="236.4656982421875" height="19" fill="black" rx="2"/><rect x="353" y="122.5" width="35.74200439453125" height="19" fill="black" rx="2"/><rect x="281.6640625" y="161" width="116.89688110351562" height="22" fill="black" rx="2"/><rect x="135.03125" y="209" width="87.7899169921875" height="22" fill="black" rx="2"/><rect x="122.6796875" y="232.5" width="112.79989624023438" height="19" fill="black" rx="2"/><rect x="296.4453125" y="209" width="86.970947265625" height="22" fill="black" rx="2"/><rect x="289.7421875" y="232.5" width="100.5618896484375" height="19" fill="black" rx="2"/><rect x="475.90625" y="209" width="50.052978515625" height="22" fill="black" rx="2"/><rect x="465.21875" y="232.5" width="72.3099365234375" height="19" fill="black" rx="2"/><rect x="228" y="303.5" width="95.43988037109375" height="19" fill="black" rx="2"/><rect x="205.9765625" y="345" width="147.34185791015625" height="22" fill="black" rx="2"/><rect x="207.265625" y="368.5" width="145.65777587890625" height="19" fill="black" rx="2"/><rect x="512" y="360.5" width="39.76995849609375" height="19" fill="black" rx="2"/><rect x="205.2265625" y="461" width="148.77389526367188" height="22" fill="black" rx="2"/><rect x="205.390625" y="484.5" width="150.19174194335938" height="19" fill="black" rx="2"/><rect x="293" y="416.5" width="69.7178955078125" height="19" fill="black" rx="2"/><rect x="101.1875" y="520.5" width="478.59130859375" height="19" fill="black" rx="2"/></mask></defs>

<!-- ═══ LAYER 1 : Android Device ═══ -->
<g style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
  <rect x="190" y="30" width="300" height="76" rx="12" stroke-width="0.5" style="fill:rgb(39, 80, 10);stroke:rgb(151, 196, 89);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="340" y="58" text-anchor="middle" dominant-baseline="central" style="fill:rgb(192, 221, 151);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">Android Device / Emulator</text>
  <text x="340" y="80" text-anchor="middle" dominant-baseline="central" style="fill:rgb(151, 196, 89);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">BehaviorTestApp — 5 anomaly scenarios</text>
</g>

<!-- Arrow 1 : ADB -->
<line x1="340" y1="106" x2="340" y2="148" marker-end="url(#arrow)" style="fill:none;stroke:rgb(156, 154, 146);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
<text x="358" y="132" dominant-baseline="central" fill="var(--color-text-secondary)" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">ADB</text>

<!-- ═══ LAYER 2 : Python Backend (container) ═══ -->
<g style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
  <rect x="80" y="148" width="520" height="138" rx="14" stroke-width="0.5" style="fill:rgb(12, 68, 124);stroke:rgb(133, 183, 235);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="340" y="172" text-anchor="middle" dominant-baseline="central" style="fill:rgb(181, 212, 244);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">Python Backend</text>
</g>

<!-- Inner boxes inside backend -->
<g style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
  <rect x="108" y="188" width="142" height="80" rx="8" stroke-width="0.5" style="fill:rgb(8, 80, 65);stroke:rgb(93, 202, 165);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="179" y="220" text-anchor="middle" dominant-baseline="central" style="fill:rgb(159, 225, 203);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">collector.py</text>
  <text x="179" y="242" text-anchor="middle" dominant-baseline="central" style="fill:rgb(93, 202, 165);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">ADB logcat reader</text>
</g>

<g style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
  <rect x="269" y="188" width="142" height="80" rx="8" stroke-width="0.5" style="fill:rgb(113, 43, 19);stroke:rgb(240, 153, 123);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="340" y="220" text-anchor="middle" dominant-baseline="central" style="fill:rgb(245, 196, 179);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">detector.py</text>
  <text x="340" y="242" text-anchor="middle" dominant-baseline="central" style="fill:rgb(240, 153, 123);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">Anomaly engine</text>
</g>

<g style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
  <rect x="430" y="188" width="142" height="80" rx="8" stroke-width="0.5" style="fill:rgb(60, 52, 137);stroke:rgb(175, 169, 236);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="501" y="220" text-anchor="middle" dominant-baseline="central" style="fill:rgb(206, 203, 246);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">api.py</text>
  <text x="501" y="242" text-anchor="middle" dominant-baseline="central" style="fill:rgb(175, 169, 236);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">Flask :5000</text>
</g>

<!-- Internal arrows between backend boxes -->
<line x1="250" y1="228" x2="267" y2="228" marker-end="url(#arrow)" style="fill:none;stroke:rgb(156, 154, 146);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
<line x1="411" y1="228" x2="428" y2="228" marker-end="url(#arrow)" style="fill:none;stroke:rgb(156, 154, 146);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

<!-- Arrow 2 : Local Inference -->
<line x1="280" y1="286" x2="280" y2="328" marker-end="url(#arrow)" mask="url(#imagine-text-gaps-vo2xp2)" style="fill:none;stroke:rgb(156, 154, 146);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
<text x="232" y="313" dominant-baseline="central" fill="var(--color-text-secondary)" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">Local inference</text>

<!-- ═══ LAYER 3 : Ollama LLM ═══ -->
<g style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
  <rect x="130" y="328" width="300" height="76" rx="12" stroke-width="0.5" style="fill:rgb(99, 56, 6);stroke:rgb(239, 159, 39);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="280" y="356" text-anchor="middle" dominant-baseline="central" style="fill:rgb(250, 199, 117);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">Ollama — phi3 (3.8B)</text>
  <text x="280" y="378" text-anchor="middle" dominant-baseline="central" style="fill:rgb(239, 159, 39);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">100% local · no data leak</text>
</g>

<!-- Arrow 3 : HTTP from api.py to dashboard -->
<path d="M501 268 L501 460 L430 460" fill="none" stroke="var(--color-text-tertiary)" stroke-width="1" marker-end="url(#arrow)" stroke-dasharray="5 3" style="fill:none;stroke:rgb(156, 154, 146);color:rgb(255, 255, 255);stroke-width:1px;stroke-dasharray:5px, 3px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
<text x="516" y="370" dominant-baseline="central" fill="var(--color-text-secondary)" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">HTTP</text>

<!-- ═══ LAYER 4 : SOC Dashboard ═══ -->
<g style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
  <rect x="130" y="444" width="300" height="76" rx="12" stroke-width="0.5" style="fill:rgb(68, 68, 65);stroke:rgb(180, 178, 169);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="280" y="472" text-anchor="middle" dominant-baseline="central" style="fill:rgb(211, 209, 199);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">SOC Web Dashboard</text>
  <text x="280" y="494" text-anchor="middle" dominant-baseline="central" style="fill:rgb(180, 178, 169);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">profiler/static/index.html</text>
</g>

<!-- Arrow 4 : from Ollama to Dashboard (analysis results) -->
<line x1="280" y1="404" x2="280" y2="442" marker-end="url(#arrow)" style="fill:none;stroke:rgb(156, 154, 146);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
<text x="298" y="426" dominant-baseline="central" fill="var(--color-text-secondary)" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">AI analysis</text>

<!-- Legend -->
<rect x="40" y="504" width="600" height="1" fill="var(--color-border-tertiary)" style="fill:rgba(222, 220, 209, 0.15);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
<text x="340" y="530" text-anchor="middle" dominant-baseline="central" fill="var(--color-text-tertiary)" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">MITRE ATT&amp;CK mapping · Weighted z-score scoring · Incident lifecycle management</text>
</svg>ndroid_behavior_analysis_architecture.svg…]()


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
