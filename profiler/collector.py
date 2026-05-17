"""
collector.py — BehaviorProfiler
ADB logcat reader with Hybrid JSON / Regex parsing and IOC Extraction.
"""

import subprocess
import threading
import time
import re
import json
from collections import deque
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

ADB_PATH        = "adb"
DEVICE_ID       = "emulator-5556"
PACKAGE         = "com.audit.behaviortestapp"
TAG_FILTER      = "BehaviorApp"
BUFFER_SIZE     = 300          
TICK_INTERVAL   = 1.0          

lock            = threading.Lock()
log_buffer      = deque(maxlen=BUFFER_SIZE)
signal_history  = deque(maxlen=60)
_ioc_rolling    = set()          # Persistent IOC set; never wiped, only grows

current_signals = {
    "rpm":          0,
    "error_rate":   0.0,
    "avg_latency":  0.0,
    "crash_count":  0,
    "storage_ops":  0,
    "retry_count":  0,
    "timestamp":    None,
    "iocs":         []
}

_tick_counters = {
    "requests":   0,
    "errors":     0,
    "latencies":  [],
    "crashes":    0,
    "storage":    0,
    "retries":    0,
    "iocs":       set()
}

def check_device():
    try:
        result = subprocess.run([ADB_PATH, "-s", DEVICE_ID, "devices"], capture_output=True, text=True, timeout=5)
        lines   = result.stdout.strip().split("\n")
        devices = [l for l in lines[1:] if l.strip() and "device" in l]
        return len(devices) > 0
    except Exception as e:
        print(Fore.RED + f"[ADB] Device check failed: {e}")
        return False

def clear_logcat():
    try:
        subprocess.run([ADB_PATH, "-s", DEVICE_ID, "logcat", "-c"], timeout=5)
        print(Fore.GREEN + "[ADB] Logcat cleared")
    except Exception as e:
        print(Fore.RED + f"[ADB] Clear failed: {e}")

def parse_log_line(line):
    global _tick_counters

    if TAG_FILTER not in line:
        return None

    entry = {
        "raw":       line.strip(),
        "time":      datetime.now().isoformat(),
        "level":     "I",
        "tag":       "",
        "message":   "",
    }

    match = re.search(r'\s([VDIWEF])\s+(BehaviorApp[.\w]*)\s*:\s*(.+)', line)
    if match:
        entry["level"]   = match.group(1)
        entry["tag"]     = match.group(2)
        entry["message"] = match.group(3)

    msg = entry["message"]
    tag = entry["tag"]

    with lock:
        # IOC Extraction: capture endpoints/paths from log messages.
        # Filter out single-word HTTP method names only — keep everything else,
        # including /status which is the retry loop target endpoint.
        GENERIC_PATHS = {"/get", "/post", "/put", "/delete", "/patch", "/head"}
        endpoints = re.findall(r'(/[a-zA-Z0-9_/.-]+)', msg)
        for ep in endpoints:
            if len(ep) > 2 and ep.lower() not in GENERIC_PATHS:
                _tick_counters["iocs"].add(ep)
                _ioc_rolling.add(ep)          # also accumulate in persistent set

        # 1. Attempt JSON parsing
        if msg.strip().startswith('{') and msg.strip().endswith('}'):
            try:
                data = json.loads(msg)
                if "Crash" in data.get("tag", "") or data.get("is_crash"):
                    _tick_counters["crashes"] += 1
                elif data.get("is_retry"):
                    _tick_counters["retries"] += 1
                    _tick_counters["requests"] += 1
                    _tick_counters["errors"] += 1
                    _tick_counters["latencies"].append(0)
                elif "Network" in data.get("tag", ""):
                    _tick_counters["requests"] += 1
                    if data.get("status", 200) >= 400:
                        _tick_counters["errors"] += 1
                    _tick_counters["latencies"].append(data.get("latency", 0))
                return entry
            except json.JSONDecodeError:
                pass 

        # 2. Fallback Regex Parsing
        if "Crash" in tag or "NPE" in msg or "CRASH" in msg:
            _tick_counters["crashes"] += 1
        elif "attempt #" in msg or "RETRY" in msg or ("retry" in msg.lower() and "Network" in tag):
            _tick_counters["retries"]  += 1
            _tick_counters["requests"] += 1
            _tick_counters["errors"]   += 1
            _tick_counters["latencies"].append(0)
        elif "Network" in tag or "NET" in msg:
            _tick_counters["requests"] += 1
            lat_match = re.search(r'in (\d+)ms', msg)
            if lat_match:
                _tick_counters["latencies"].append(int(lat_match.group(1)))
            elif "failed" in msg.lower() or "→ 4" in msg or "→ 5" in msg:
                _tick_counters["errors"]   += 1
                _tick_counters["latencies"].append(0)
        
        if "Storage" in tag or "Wrote to" in msg or "READ" in msg or "WRITE" in msg:
            _tick_counters["storage"] += 1

    return entry

def signal_ticker():
    global _tick_counters, current_signals

    while True:
        time.sleep(TICK_INTERVAL)
        with lock:
            reqs    = _tick_counters["requests"]
            errs    = _tick_counters["errors"]
            lats    = _tick_counters["latencies"]
            crashes = _tick_counters["crashes"]
            storage = _tick_counters["storage"]
            retries = _tick_counters["retries"]
            iocs    = list(_tick_counters["iocs"])

            rpm        = reqs * 60
            error_rate = (errs / reqs * 100) if reqs > 0 else 0.0
            real_lats  = [l for l in lats if l > 0]
            avg_lat    = (sum(real_lats) / len(real_lats)) if real_lats else 0.0

            snapshot = {
                "timestamp":    datetime.now().isoformat(),
                "rpm":          rpm,
                "error_rate":   round(error_rate, 2),
                "avg_latency":  round(avg_lat, 2),
                "crash_count":  crashes,
                "storage_ops":  storage,
                "retry_count":  retries,
                "iocs":         list(_ioc_rolling)   # always the full accumulated set
            }

            current_signals.update(snapshot)
            signal_history.append(snapshot)

            _tick_counters = {k: 0 if isinstance(v, int) else ([] if isinstance(v, list) else set()) for k, v in _tick_counters.items()}

def logcat_reader():
    cmd = [ADB_PATH, "-s", DEVICE_ID, "logcat", "-v", "threadtime"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        for line in proc.stdout:
            entry = parse_log_line(line)
            if entry:
                with lock:
                    log_buffer.append(entry)
    except Exception as e:
        print(Fore.RED + f"[ADB] Logcat reader crashed: {e}")
    finally:
        proc.terminate() 

def get_current_signals():
    with lock: return dict(current_signals)

def get_signal_history():
    with lock: return list(signal_history)

def get_recent_logs(n=50):
    with lock: return list(log_buffer)[-n:]

def start_collector():
    if not check_device(): return False
    clear_logcat()
    threading.Thread(target=logcat_reader, daemon=True).start()
    threading.Thread(target=signal_ticker, daemon=True).start()
    return True