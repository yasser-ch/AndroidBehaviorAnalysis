"""
detector.py — BehaviorProfiler
Anomaly detection with MITRE ATT&CK Mapping, Triage workflows, and Trigger Context.
"""

import threading
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

INCIDENT_GAP_SEC = 60   # close stale incidents after 60 s of silence (was 30 — too aggressive)

DEFAULT_BASELINE = {
    "rpm": 60.0, "error_rate": 2.0, "avg_latency": 200.0,
    "crash_count": 0.0, "storage_ops": 2.0, "retry_count": 0.0,
}

WEIGHTS = {"rpm": 0.05, "error_rate": 0.35, "avg_latency": 0.05, "crash_count": 0.40, "retry_count": 0.15}
THRESHOLDS = {"rpm": 3.0, "error_rate": 4.0, "avg_latency": 4.0, "crash_count": 1.0, "retry_count": 3.0}
CEILINGS = {"rpm": 10.0, "error_rate": 15.0, "avg_latency": 10.0, "crash_count": 5.0, "retry_count": 10.0}

RULES = [
    {
        "id": "logic_bomb_exfil",
        "name": "Data Exfiltration Pattern",
        "severity": "critical",
        "mitre_id": "T1048",
        "mitre_tactic": "Exfiltration Over Alternative Protocol",
        "check": lambda s, b: s["storage_ops"] > max(b["storage_ops"] * 4, 10) and s["rpm"] > max(b["rpm"] * 2, 100),
        "description": "High storage reads instantly followed by a network spike — potential data exfiltration."
    },
    {
        "id": "silent_hang",
        "name": "Silent Application Hang",
        "severity": "high",
        "mitre_id": "T1499",
        "mitre_tactic": "Endpoint Denial of Service",
        "check": lambda s, b: s["avg_latency"] > max(b["avg_latency"] * 5, 1500) and s["error_rate"] == 0 and s["rpm"] > 0,
        "description": "Extreme latency with zero errors. The application thread is hanging but not crashing."
    },
    {
        "id": "infinite_retry",
        "name": "Infinite Retry Loop",
        "severity": "high",
        "mitre_id": "T1071.001",
        "mitre_tactic": "Web Protocol Abuse (Client Bug)",
        "check": lambda s, b: s["retry_count"] > max(b["retry_count"] * 3, 2) and s["error_rate"] > 20,
        "description": "App is stuck retrying a failing request with no exponential backoff."
    },
    {
        "id": "request_spam",
        "name": "Request Spam",
        "severity": "high",
        "mitre_id": "T1498",
        "mitre_tactic": "Network Denial of Service",
        "check": lambda s, b: s["rpm"] > max(b["rpm"] * 4, 200) and s["error_rate"] < 30,
        "description": "Request rate is 4× above baseline — possible runaway background job."
    },
    {
        "id": "crash_storm",
        "name": "Crash Storm",
        "severity": "high",
        "mitre_id": "T1499.004",
        "mitre_tactic": "Application Exploitation (Stability)",
        "check": lambda s, b: s["crash_count"] >= 3,
        "description": "Multiple crashes detected instantly — unhandled exception loop."
    },
    {
        "id": "timeout_pattern",
        "name": "Timeout / Slow Response",
        "severity": "medium",
        "mitre_id": "T1499",
        "mitre_tactic": "Endpoint Denial of Service",
        "check": lambda s, b: s["avg_latency"] > max(b["avg_latency"] * 4, 800) and s["rpm"] < max(b["rpm"] * 0.6, 1),
        "description": "Latency spikes causing the client to back off."
    }
]

state_lock        = threading.Lock()
baseline          = dict(DEFAULT_BASELINE)
baseline_locked   = False
_baseline_samples = []
_clean_streak     = 0

incident_log    = []
_open_incidents = {}
_latest_score   = 0.0          # always the most-recent tick's anomaly score

def _is_clean(snapshot):
    return snapshot.get("error_rate", 0) < 5 and snapshot.get("crash_count", 0) == 0 and snapshot.get("retry_count", 0) == 0

def update_baseline(snapshot):
    global baseline, baseline_locked, _baseline_samples, _clean_streak

    if baseline_locked: return
    if _is_clean(snapshot):
        _clean_streak += 1
        _baseline_samples.append(snapshot)
    else:
        _clean_streak = 0
        _baseline_samples.clear()
        return

    if _clean_streak >= 30:
        for key in DEFAULT_BASELINE:
            vals = [s[key] for s in _baseline_samples if key in s]
            if vals: baseline[key] = sum(vals) / len(vals)
        baseline_locked = True

def compute_score(snapshot):
    """
    Pure function: returns the anomaly score for THIS tick only (0-100).
    No decay, no state mutation. Score reflects current signal intensity.
    Returns 0.0 before baseline is locked — meaningless to score without a reference.
    """
    if not baseline_locked:
        return 0.0, {f: 0.0 for f in WEIGHTS}

    feature_scores = {}
    total = 0.0

    for feature in WEIGHTS:
        current = snapshot.get(feature, 0.0)
        base    = baseline.get(feature, DEFAULT_BASELINE.get(feature, 1.0))
        dev     = CEILINGS[feature] if (base <= 0 and current > 0) else (0.0 if base <= 0 else current / base)

        lo, hi, w = THRESHOLDS[feature], CEILINGS[feature], WEIGHTS[feature]
        contrib   = 0.0 if dev <= lo else (w * 100.0 if dev >= hi else w * 100.0 * (dev - lo) / (hi - lo))

        feature_scores[feature] = round(contrib, 2)
        total += contrib

    return round(min(total, 100.0), 2), feature_scores

def match_rules(snapshot):
    return [r for r in RULES if r["check"](snapshot, baseline)]

def _close_stale_incidents():
    now_dt = datetime.now()
    stale = []
    for rid, inc in _open_incidents.items():
        if (now_dt - datetime.fromisoformat(inc["last_seen"])).total_seconds() >= INCIDENT_GAP_SEC:
            stale.append(rid)
            
    for rid in stale:
        incident = _open_incidents.pop(rid)
        incident["status"] = "closed"
        incident["duration_sec"] = (datetime.fromisoformat(incident["last_seen"]) - datetime.fromisoformat(incident["first_seen"])).total_seconds()
        incident_log.append(incident)

def _update_incidents(triggered_rules, score, timestamp, snapshot):
    iocs = snapshot.get("iocs", [])
    
    for rule in triggered_rules:
        rid = rule["id"]

        # Suppress new events for rules that have been triaged as false positives.
        # Check BOTH open and closed incidents — a user may mark an open incident
        # as false_positive before it closes, which previously was invisible here.
        already_fp = (
            any(i["rule_id"] == rid and i["triage_status"] == "false_positive"
                for i in incident_log[-20:]) or
            (rid in _open_incidents and
             _open_incidents[rid].get("triage_status") == "false_positive")
        )
        if already_fp:
            continue

        if rid in _open_incidents:
            inc = _open_incidents[rid]
            inc["last_seen"] = timestamp
            inc["event_count"] += 1
            inc["peak_score"] = max(inc["peak_score"], score)
            inc["latest_score"] = score
            inc["duration_sec"] = (datetime.fromisoformat(timestamp) - datetime.fromisoformat(inc["first_seen"])).total_seconds()
            if iocs: inc["iocs"].extend([i for i in iocs if i not in inc["iocs"]])
        else:
            # Capture the exact state of metrics when this triggered
            trigger_context = {k: snapshot.get(k, 0) for k in ["rpm", "error_rate", "avg_latency", "crash_count", "retry_count", "storage_ops"]}
            
            _open_incidents[rid] = {
                "incident_id": f"{rid}-{timestamp}", "rule_id": rid, "rule_name": rule["name"],
                "severity": rule["severity"], "description": rule["description"], 
                "mitre_id": rule["mitre_id"], "mitre_tactic": rule["mitre_tactic"],
                "first_seen": timestamp, "last_seen": timestamp, "event_count": 1, 
                "peak_score": score, "latest_score": score, "duration_sec": 0.0, 
                "status": "open", "triage_status": "new", "iocs": iocs or [],
                "trigger_context": trigger_context
            }
    return list(_open_incidents.values())

def analyze(snapshot):
    global _latest_score
    with state_lock:
        ts = snapshot.get("timestamp") or datetime.now().isoformat()
        update_baseline(snapshot)
        _close_stale_incidents()

        score, feature_scores = compute_score(snapshot)
        _latest_score = score                    # keep the live value accessible
        triggered_rules = match_rules(snapshot)

        if any(r["severity"] == "critical" for r in triggered_rules): severity = "critical"
        elif any(r["severity"] == "high" for r in triggered_rules): severity = "high"
        elif any(r["severity"] == "medium" for r in triggered_rules): severity = "medium"
        elif any(r["severity"] == "low" for r in triggered_rules): severity = "low"
        else: severity = "normal"

        open_incidents = _update_incidents(triggered_rules, score, ts, snapshot) if triggered_rules else list(_open_incidents.values())

        return {
            "timestamp": ts, "score": score, "severity": severity,
            "feature_scores": feature_scores, "triggered_rules": triggered_rules,
            "open_incidents": open_incidents, "baseline_locked": baseline_locked,
            "baseline": dict(baseline), "signals": snapshot,
        }

def get_incidents():
    with state_lock:
        _close_stale_incidents()
        return list(incident_log) + list(_open_incidents.values())

def get_open_incidents():
    with state_lock: return list(_open_incidents.values())

def get_baseline():
    with state_lock: return dict(baseline)

def is_baseline_locked():
    with state_lock: return baseline_locked

def get_latest_score():
    with state_lock: return _latest_score

def triage_incident(incident_id, status):
    with state_lock:
        for inc in _open_incidents.values():
            if inc["incident_id"] == incident_id:
                inc["triage_status"] = status
                return True
        for inc in incident_log:
            if inc["incident_id"] == incident_id:
                inc["triage_status"] = status
                return True
    return False