"""
api.py — BehaviorProfiler
Flask REST API with Threat Intelligence context.
"""

import requests as req
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import threading
import time

from collector import start_collector, get_current_signals, get_signal_history, get_recent_logs
from detector import analyze, get_incidents, get_open_incidents, get_baseline, is_baseline_locked, triage_incident, get_latest_score

app  = Flask(__name__)
CORS(app)
_latest_result = {}

def analysis_loop():
    global _latest_result
    while True:
        time.sleep(1)
        try:
            snapshot = get_current_signals()
            if snapshot.get("timestamp"):
                _latest_result = analyze(snapshot)
        except Exception as e:
            pass

@app.route("/api/status")
def status():
    return jsonify({"status": "running", "baseline_locked": is_baseline_locked(), "baseline": get_baseline()})

@app.route("/api/signals/current")
def signals_current():
    sig = get_current_signals()
    sig["anomaly_score"] = round(get_latest_score(), 1)   # inject live score
    return jsonify(sig)

@app.route("/api/signals/history")
def signals_history(): return jsonify(get_signal_history())

@app.route("/api/logs")
def logs(): return jsonify(get_recent_logs(50))

@app.route("/api/incidents")
@app.route("/api/anomalies")
def incidents(): return jsonify(get_incidents())

@app.route("/api/incidents/<incident_id>/triage", methods=["POST"])
def triage(incident_id):
    data = request.json
    status = data.get("status")
    if triage_incident(incident_id, status):
        return jsonify({"status": "ok", "message": f"Incident marked as {status}"})
    return jsonify({"status": "error", "message": "Incident not found"}), 404

@app.route("/api/analyze", methods=["POST"])
def analyze_ai():
    try:
        signals = get_current_signals()
        baseline = get_baseline()
        open_incidents = get_open_incidents()
        all_incidents = get_incidents()

        def _fmt_duration(inc):
            dur = inc.get("duration_sec", 0.0)
            return f"{int(dur // 60)}m {int(dur % 60)}s" if dur >= 60 else f"{int(dur)}s"

        target_incidents = open_incidents if open_incidents else all_incidents[-3:]
        
        if target_incidents:
            incident_summary = "\n".join([
                f"- {inc['rule_name']} ({inc['severity'].upper()}): "
                f"MITRE {inc.get('mitre_id','N/A')} ({inc.get('mitre_tactic','N/A')}). "
                f"{inc['event_count']} events, {_fmt_duration(inc)}. "
                f"IOCs: {', '.join(inc.get('iocs', [])) or 'None'}."
                for inc in target_incidents
            ])
        else:
            incident_summary = "No anomalies — behavior normal."

        prompt = f"""SOC Tier 2 analyst. Be concise. Max 200 words total.

ACTIVE INCIDENTS:
{incident_summary}

SIGNALS: rpm={signals.get('rpm',0)} (baseline {round(baseline.get('rpm',0))}), error={signals.get('error_rate',0):.1f}% (baseline {baseline.get('error_rate',0):.1f}%)

Answer in exactly this format:
1. ROOT CAUSE & MITRE: [1-2 sentences max]
2. IOC ANALYSIS: [1 sentence]
3. REMEDIATION: a) [action] b) [action]
"""

        # --- Local-first: query Ollama for installed models, then pick the best one ---
        local_response = None
        used_model = None

        # Probe which models are actually installed — avoids 30s timeouts per missing model
        installed_models = set()
        try:
            tags_r = req.get("http://localhost:11434/api/tags", timeout=3)
            if tags_r.status_code == 200:
                for m in tags_r.json().get("models", []):
                    installed_models.add(m.get("name", "").split(":")[0])
        except Exception:
            pass  # Ollama not running — will skip straight to fallback

        # Preference order — pick the smallest/fastest model available on the GPU
        preferred = ["phi3", "gemma", "mistral", "llama3", "llama2", "tinyllama"]
        candidates = [m for m in preferred if m in installed_models]
        # If none of the preferred list matched, try whatever IS installed
        if not candidates and installed_models:
            candidates = list(installed_models)[:2]

        for model in candidates:
            try:
                r = req.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "num_predict": 300,        # tighter budget → faster on RTX 4050
                        "options": {
                            "temperature": 0.2,    # lower temp = more deterministic, faster
                            "num_ctx": 1024,       # small context window → less VRAM pressure
                        }
                    },
                    timeout=45,                    # single model now, 45s is generous
                )
                if r.status_code == 200:
                    text = r.json().get("response", "").strip()
                    if text:
                        local_response = text
                        used_model = model
                        break
            except Exception:
                continue

        if local_response:
            return jsonify({"status": "ok", "analysis": local_response, "model": used_model})

        # --- Fallback: rule-based deterministic analysis (no external API needed) ---
        lines = ["[Rule-Based SOC Analysis — Ollama unavailable]\n"]

        if not target_incidents or incident_summary.startswith("No anomalies"):
            lines.append("1. ROOT CAUSE: No active anomalies detected. Signals appear within baseline parameters.")
            lines.append("2. IOC ANALYSIS: No targeted endpoints identified at this time.")
            lines.append("3. REMEDIATION: Continue monitoring. Ensure baseline has fully converged (≥30 clean ticks).")
        else:
            severities = [i["severity"] for i in target_incidents]
            mitre_ids  = list({i.get("mitre_id","N/A") for i in target_incidents})
            all_iocs   = list({ioc for i in target_incidents for ioc in i.get("iocs", [])})
            top_inc    = max(target_incidents, key=lambda i: i.get("peak_score", 0))

            lines.append(f"1. ROOT CAUSE & MITRE ALIGNMENT:")
            lines.append(f"   The dominant incident is '{top_inc['rule_name']}' (score {round(top_inc.get('peak_score',0))}).")
            lines.append(f"   Mapped MITRE techniques: {', '.join(mitre_ids)}.")
            lines.append(f"   Combined severity profile: {', '.join(set(severities)).upper()}.")

            lines.append(f"\n2. IOC ANALYSIS:")
            if all_iocs:
                lines.append(f"   Targeted endpoints detected: {', '.join(all_iocs)}")
                lines.append(f"   These paths appear in {len(target_incidents)} incident(s) — monitor for exfiltration or C2 patterns.")
            else:
                lines.append("   No specific endpoint IOCs extracted. Attack may be volumetric rather than path-targeted.")

            lines.append(f"\n3. REMEDIATION:")
            if any(i["rule_id"] == "infinite_retry" for i in target_incidents):
                lines.append("   a) Implement exponential backoff with jitter in the client — the retry storm is self-inflicted.")
                lines.append("   b) Apply a circuit-breaker pattern: block outbound retries after 3 consecutive failures.")
            elif any(i["rule_id"] == "request_spam" for i in target_incidents):
                lines.append("   a) Rate-limit outbound requests from the app process at the OS level (iptables or traffic shaping).")
                lines.append("   b) Identify and kill the runaway background job or service thread causing the spike.")
            elif any(i["rule_id"] == "logic_bomb_exfil" for i in target_incidents):
                lines.append("   a) Immediately block egress on the identified IOC endpoints at the network firewall.")
                lines.append("   b) Capture a full memory dump and network pcap before killing the process for forensics.")
            else:
                lines.append("   a) Isolate the affected process and capture logs before remediation.")
                lines.append("   b) Review recent code deployments for the introducing commit and roll back if necessary.")

        return jsonify({"status": "ok", "analysis": "\n".join(lines), "model": "rule-based (Ollama offline)"})

    except Exception as e:
        return jsonify({"status": "error", "analysis": f"Analysis failed: {e}", "model": "error"}), 500

@app.route("/api/analyze/stream", methods=["POST"])
def analyze_ai_stream():
    """
    SSE streaming version of /api/analyze.
    Emits tokens as they arrive from Ollama so the UI updates in real-time
    instead of waiting for the full generation to complete.
    Falls back to the rule-based engine if Ollama is unavailable.
    """
    import json as _json

    def _build_context():
        signals       = get_current_signals()
        baseline_data = get_baseline()
        open_incidents = get_open_incidents()
        all_incidents  = get_incidents()

        def _fmt(inc):
            dur = inc.get("duration_sec", 0.0)
            return f"{int(dur//60)}m {int(dur%60)}s" if dur >= 60 else f"{int(dur)}s"

        targets = open_incidents if open_incidents else all_incidents[-3:]
        summary = "\n".join([
            f"- {i['rule_name']} ({i['severity'].upper()}): MITRE {i.get('mitre_id','N/A')}. "
            f"{i['event_count']} events, {_fmt(i)}. IOCs: {', '.join(i.get('iocs',[])) or 'None'}."
            for i in targets
        ]) if targets else "No anomalies — behavior normal."

        prompt = f"""SOC Tier 2 analyst. Be concise. Max 200 words.

ACTIVE INCIDENTS:
{summary}

SIGNALS: rpm={signals.get('rpm',0)} (baseline {round(baseline_data.get('rpm',0))}), error={signals.get('error_rate',0):.1f}%

Answer in exactly this format:
1. ROOT CAUSE & MITRE: [1-2 sentences]
2. IOC ANALYSIS: [1 sentence]
3. REMEDIATION: a) [action] b) [action]
"""
        return prompt, targets

    def generate():
        prompt, targets = _build_context()

        # Check installed models
        installed = set()
        try:
            t = req.get("http://localhost:11434/api/tags", timeout=3)
            if t.status_code == 200:
                for m in t.json().get("models", []):
                    installed.add(m.get("name","").split(":")[0])
        except Exception:
            pass

        preferred  = ["phi3", "gemma", "mistral", "llama3", "tinyllama"]
        candidates = [m for m in preferred if m in installed] or list(installed)[:1]

        if candidates:
            model = candidates[0]
            yield f"data: {_json.dumps({'type':'model','model':model})}\n\n"
            try:
                with req.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model, "prompt": prompt, "stream": True,
                        "num_predict": 300,
                        "options": {"temperature": 0.2, "num_ctx": 1024}
                    },
                    stream=True, timeout=60
                ) as r:
                    for line in r.iter_lines():
                        if line:
                            chunk = _json.loads(line)
                            token = chunk.get("response", "")
                            if token:
                                yield f"data: {_json.dumps({'type':'token','text':token})}\n\n"
                            if chunk.get("done"):
                                yield f"data: {_json.dumps({'type':'done','model':model})}\n\n"
                                return
            except Exception as e:
                yield f"data: {_json.dumps({'type':'error','text':str(e)})}\n\n"
                # fall through to rule-based

        # Rule-based fallback — emit as a single chunk
        lines = ["[Rule-Based SOC Analysis — Ollama unavailable]\n"]
        if not targets:
            lines += [
                "1. ROOT CAUSE: No active anomalies. Signals within baseline.",
                "2. IOC ANALYSIS: No targeted endpoints identified.",
                "3. REMEDIATION: Continue monitoring; ensure baseline has converged.",
            ]
        else:
            all_iocs  = list({ioc for i in targets for ioc in i.get("iocs",[])})
            mitre_ids = list({i.get("mitre_id","N/A") for i in targets})
            top       = max(targets, key=lambda i: i.get("peak_score",0))
            lines += [
                f"1. ROOT CAUSE & MITRE: Dominant incident '{top['rule_name']}'. Techniques: {', '.join(mitre_ids)}.",
                f"2. IOC ANALYSIS: {'Endpoints: ' + ', '.join(all_iocs) if all_iocs else 'No specific IOCs — likely volumetric.'}",
            ]
            if any(i["rule_id"]=="infinite_retry" for i in targets):
                lines.append("3. REMEDIATION: a) Add exponential backoff + jitter. b) Apply circuit-breaker after 3 failures.")
            elif any(i["rule_id"]=="request_spam" for i in targets):
                lines.append("3. REMEDIATION: a) Rate-limit at OS level (iptables). b) Kill runaway background thread.")
            elif any(i["rule_id"]=="logic_bomb_exfil" for i in targets):
                lines.append("3. REMEDIATION: a) Block egress on IOC endpoints. b) Capture memory dump + pcap for forensics.")
            else:
                lines.append("3. REMEDIATION: a) Isolate process and capture logs. b) Review recent deploys and roll back.")

        fallback_text = "\n".join(lines)
        yield f"data: {_json.dumps({'type':'token','text':fallback_text})}\n\n"
        yield f"data: {_json.dumps({'type':'done','model':'rule-based'})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/ollama/status")
def ollama_status():
    """Probe Ollama and return available models — used by the UI status line."""
    try:
        r = req.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m.get("name", "") for m in r.json().get("models", [])]
            preferred = ["phi3", "gemma", "mistral", "llama3", "llama2", "tinyllama"]
            active = next((m for p in preferred for m in models if m.startswith(p)), models[0] if models else None)
            return jsonify({"status": "online", "models": models, "active": active})
    except Exception:
        pass
    return jsonify({"status": "offline", "models": [], "active": None})


@app.route("/api/chat", methods=["POST"])
def chat_proxy():
    """
    SSE streaming proxy: browser → Flask → Ollama /api/chat.
    Sidesteps browser CORS restriction on direct localhost:11434 calls.
    Body JSON: { "messages": [...], "model": "phi3" (optional) }
    """
    import json as _json

    data = request.json or {}
    messages = data.get("messages", [])
    requested_model = data.get("model")

    # Resolve model if not specified
    model = requested_model
    if not model:
        try:
            tags_r = req.get("http://localhost:11434/api/tags", timeout=3)
            if tags_r.status_code == 200:
                installed = [m.get("name", "") for m in tags_r.json().get("models", [])]
                preferred = ["phi3", "gemma", "mistral", "llama3", "tinyllama"]
                model = next((m for p in preferred for m in installed if m.startswith(p)), installed[0] if installed else None)
        except Exception:
            pass

    if not model:
        return jsonify({"error": "Ollama offline or no models installed"}), 503

    def generate():
        try:
            with req.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": {"temperature": 0.45, "num_ctx": 4096, "num_predict": 600}
                },
                stream=True, timeout=120
            ) as r:
                yield f"data: {_json.dumps({'type': 'model', 'model': model})}\n\n"
                for line in r.iter_lines():
                    if line:
                        try:
                            chunk = _json.loads(line)
                            tok = chunk.get("message", {}).get("content", "")
                            if tok:
                                yield f"data: {_json.dumps({'type': 'token', 'text': tok})}\n\n"
                            if chunk.get("done"):
                                yield f"data: {_json.dumps({'type': 'done', 'model': model})}\n\n"
                                return
                        except Exception:
                            pass
        except Exception as e:
            yield f"data: {_json.dumps({'type': 'error', 'text': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def start_server():
    if not start_collector(): return
    threading.Thread(target=analysis_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)