import subprocess, platform, time, datetime as dt, requests

DEVICES = {
    "ac:cc:8e:ab:35:27": {"name": "RealCamera01", "ip": "10.10.1.47", "type": "camera", "site": "Test Bench"},

    "00:1A:2B:3C:50:00": {"name": "OfficeCam01", "ip": "10.10.1.11",  "type": "camera", "site": "Office"},
    "00:1A:2B:3C:50:01": {"name": "OfficeCam02", "ip": "10.10.1.12",  "type": "camera", "site": "Office"},
    "00:1A:2B:3C:50:02": {"name": "OfficeCam03", "ip": "10.10.1.13",  "type": "camera", "site": "Office"},
    "00:1A:2B:3C:50:03": {"name": "OfficeCam04", "ip": "10.10.1.14",  "type": "camera", "site": "Office"},
    "00:1A:2B:3C:50:04": {"name": "OfficeCam05", "ip": "10.10.1.15",  "type": "camera", "site": "Office"},
    "00:1A:2B:3C:50:05": {"name": "OfficeCam06", "ip": "10.10.1.16",  "type": "camera", "site": "Office"},
    "00:1A:2B:3C:50:06": {"name": "OfficeCam07", "ip": "10.10.1.17",  "type": "camera", "site": "Office"},

    "00:1A:2B:3C:50:07": {"name": "LakeHouseCam01", "ip": "10.10.2.11", "type": "camera", "site": "Lake House"},
    "00:1A:2B:3C:50:08": {"name": "LakeHouseCam02", "ip": "10.10.2.12", "type": "camera", "site": "Lake House"},
    "00:1A:2B:3C:50:09": {"name": "LakeHouseCam03", "ip": "10.10.2.13", "type": "camera", "site": "Lake House"},
    "00:1A:2B:3C:50:0A": {"name": "LakeHouseCam04", "ip": "10.10.2.14", "type": "camera", "site": "Lake House"},
    "00:1A:2B:3C:50:0B": {"name": "LakeHouseCam05", "ip": "10.10.2.15", "type": "camera", "site": "Lake House"},
    "00:1A:2B:3C:50:0C": {"name": "LakeHouseCam06", "ip": "10.10.2.16", "type": "camera", "site": "Lake House"},
    "00:1A:2B:3C:50:0D": {"name": "LakeHouseCam07", "ip": "10.10.2.17", "type": "camera", "site": "Lake House"},

    "00:1A:2B:3C:50:0E": {"name": "House1Cam01", "ip": "10.10.3.11", "type": "camera", "site": "House1"},
    "00:1A:2B:3C:50:0F": {"name": "House1Cam02", "ip": "10.10.3.12", "type": "camera", "site": "House1"},
    "00:1A:2B:3C:50:10": {"name": "House1Cam03", "ip": "10.10.3.13", "type": "camera", "site": "House1"},
    "00:1A:2B:3C:50:11": {"name": "House1Cam04", "ip": "10.10.3.14", "type": "camera", "site": "House1"},
    "00:1A:2B:3C:50:12": {"name": "House1Cam05", "ip": "10.10.3.15", "type": "camera", "site": "House1"},
    "00:1A:2B:3C:50:13": {"name": "House1Cam06", "ip": "10.10.3.16", "type": "camera", "site": "House1"},
    "00:1A:2B:3C:50:14": {"name": "House1Cam07", "ip": "10.10.3.17", "type": "camera", "site": "House1"},

    "00:1A:2B:3C:50:15": {"name": "House2Cam01", "ip": "10.10.4.11", "type": "camera", "site": "House2"},
    "00:1A:2B:3C:50:16": {"name": "House2Cam02", "ip": "10.10.4.12", "type": "camera", "site": "House2"},
    "00:1A:2B:3C:50:17": {"name": "House2Cam03", "ip": "10.10.4.13", "type": "camera", "site": "House2"},
    "00:1A:2B:3C:50:18": {"name": "House2Cam04", "ip": "10.10.4.14", "type": "camera", "site": "House2"},
    "00:1A:2B:3C:50:19": {"name": "House2Cam05", "ip": "10.10.4.15", "type": "camera", "site": "House2"},
    "00:1A:2B:3C:50:1A": {"name": "House2Cam06", "ip": "10.10.4.16", "type": "camera", "site": "House2"},
    "00:1A:2B:3C:50:1B": {"name": "House2Cam07", "ip": "10.10.4.17", "type": "camera", "site": "House2"},

    "00:1A:2B:3C:50:1C": {"name": "House3Cam01", "ip": "10.10.5.11", "type": "camera", "site": "House3"},
    "00:1A:2B:3C:50:1D": {"name": "House3Cam02", "ip": "10.10.5.12", "type": "camera", "site": "House3"},
    "00:1A:2B:3C:50:1E": {"name": "House3Cam03", "ip": "10.10.5.13", "type": "camera", "site": "House3"},
    "00:1A:2B:3C:50:1F": {"name": "House3Cam04", "ip": "10.10.5.14", "type": "camera", "site": "House3"},
    "00:1A:2B:3C:50:20": {"name": "House3Cam05", "ip": "10.10.5.15", "type": "camera", "site": "House3"},
    "00:1A:2B:3C:50:21": {"name": "House3Cam06", "ip": "10.10.5.16", "type": "camera", "site": "House3"},
    "00:1A:2B:3C:50:22": {"name": "House3Cam07", "ip": "10.10.5.17", "type": "camera", "site": "House3"},

}

API_BASE = "http://54.196.221.164:8000"
SNAPSHOT_ENDPOINT = f"{API_BASE}/snapshot"   # you'll add this on the server
PING_COUNT = "1"
PING_TIMEOUT_SEC = 2
SWEEP_INTERVAL_SEC = 300                     # ~5 minutes

def now_iso():
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

def is_up(host: str) -> bool:
    sys = platform.system().lower()
    if "windows" in sys:
        cmd = ["ping", "-4", "-n", PING_COUNT, "-w", str(PING_TIMEOUT_SEC * 1000), host]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = "TTL=" in r.stdout  # true echo reply only
        return ok
    else:
        cmd = ["ping", "-c", PING_COUNT, "-W", str(PING_TIMEOUT_SEC), host]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = "1 received" in r.stdout or "bytes from" in r.stdout
        return ok

def post(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"POST {url} -> {r.status_code} {r.text[:200]}")
        return r.ok
    except Exception as e:
        print(f"POST {url} FAILED: {e}")
        return False

# --- main loop: build one snapshot and POST it ---
while True:
    started = time.time()
    generated_at = now_iso()
    devices_out = []
    for mac, dev in DEVICES.items():
        status = "up" if is_up(dev["ip"]) else "down"
        devices_out.append({
            "mac": mac,
            "site": dev["site"],
            "type": dev["type"],
            "name": dev["name"],
            "ip": dev["ip"],
            "status": status,
            "observed_at": generated_at   # when this status was observed
        })

    snapshot = {
        "site": "SitePC-01",              # set a real site ID/name
        "generated_at": generated_at,     # ISO-8601 UTC
        "devices": devices_out,           # full set, every sweep
        "totals": {
            "count": len(devices_out),
            "down": sum(1 for d in devices_out if d["status"] == "down"),
            "up":   sum(1 for d in devices_out if d["status"] == "up"),
        }
    }

    post(SNAPSHOT_ENDPOINT, snapshot)

    time.sleep(SWEEP_INTERVAL_SEC)
