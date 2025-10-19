import subprocess, platform, time, datetime as dt, requests

DEVICES = {
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

    "00:1A:2B:3C:50:23": {"name": "House4Cam01", "ip": "10.10.6.11", "type": "camera", "site": "House4"},
    "00:1A:2B:3C:50:24": {"name": "House4Cam02", "ip": "10.10.6.12", "type": "camera", "site": "House4"},
    "00:1A:2B:3C:50:25": {"name": "House4Cam03", "ip": "10.10.6.13", "type": "camera", "site": "House4"},
    "00:1A:2B:3C:50:26": {"name": "House4Cam04", "ip": "10.10.6.14", "type": "camera", "site": "House4"},
    "00:1A:2B:3C:50:27": {"name": "House4Cam05", "ip": "10.10.6.15", "type": "camera", "site": "House4"},
    "00:1A:2B:3C:50:28": {"name": "House4Cam06", "ip": "10.10.6.16", "type": "camera", "site": "House4"},
    "00:1A:2B:3C:50:29": {"name": "House4Cam07", "ip": "10.10.6.17", "type": "camera", "site": "House4"},

    "00:1A:2B:3C:50:2A": {"name": "House5Cam01", "ip": "10.10.7.11", "type": "camera", "site": "House5"},
    "00:1A:2B:3C:50:2B": {"name": "House5Cam02", "ip": "10.10.7.12", "type": "camera", "site": "House5"},
    "00:1A:2B:3C:50:2C": {"name": "House5Cam03", "ip": "10.10.7.13", "type": "camera", "site": "House5"},
    "00:1A:2B:3C:50:2D": {"name": "House5Cam04", "ip": "10.10.7.14", "type": "camera", "site": "House5"},
    "00:1A:2B:3C:50:2E": {"name": "House5Cam05", "ip": "10.10.7.15", "type": "camera", "site": "House5"},
    "00:1A:2B:3C:50:2F": {"name": "House5Cam06", "ip": "10.10.7.16", "type": "camera", "site": "House5"},
    "00:1A:2B:3C:50:30": {"name": "House5Cam07", "ip": "10.10.7.17", "type": "camera", "site": "House5"},

    "00:1A:2B:3C:50:31": {"name": "WarehouseCam01", "ip": "10.10.8.11", "type": "camera", "site": "Warehouse"},
    "00:1A:2B:3C:50:32": {"name": "WarehouseCam02", "ip": "10.10.8.12", "type": "camera", "site": "Warehouse"},
    "00:1A:2B:3C:50:33": {"name": "WarehouseCam03", "ip": "10.10.8.13", "type": "camera", "site": "Warehouse"},
    "00:1A:2B:3C:50:34": {"name": "WarehouseCam04", "ip": "10.10.8.14", "type": "camera", "site": "Warehouse"},
    "00:1A:2B:3C:50:35": {"name": "WarehouseCam05", "ip": "10.10.8.15", "type": "camera", "site": "Warehouse"},
    "00:1A:2B:3C:50:36": {"name": "WarehouseCam06", "ip": "10.10.8.16", "type": "camera", "site": "Warehouse"},
    "00:1A:2B:3C:50:37": {"name": "WarehouseCam07", "ip": "10.10.8.17", "type": "camera", "site": "Warehouse"},

    "00:1A:2B:3C:50:38": {"name": "StudioCam01", "ip": "10.10.9.11", "type": "camera", "site": "Studio"},
    "00:1A:2B:3C:50:39": {"name": "StudioCam02", "ip": "10.10.9.12", "type": "camera", "site": "Studio"},
    "00:1A:2B:3C:50:3A": {"name": "StudioCam03", "ip": "10.10.9.13", "type": "camera", "site": "Studio"},
    "00:1A:2B:3C:50:3B": {"name": "StudioCam04", "ip": "10.10.9.14", "type": "camera", "site": "Studio"},
    "00:1A:2B:3C:50:3C": {"name": "StudioCam05", "ip": "10.10.9.15", "type": "camera", "site": "Studio"},
    "00:1A:2B:3C:50:3D": {"name": "StudioCam06", "ip": "10.10.9.16", "type": "camera", "site": "Studio"},
    "00:1A:2B:3C:50:3E": {"name": "StudioCam07", "ip": "10.10.9.17", "type": "camera", "site": "Studio"},

    "00:1A:2B:3C:50:3F": {"name": "FarmCam01", "ip": "10.10.10.11", "type": "camera", "site": "Farm"},
    "00:1A:2B:3C:50:40": {"name": "FarmCam02", "ip": "10.10.10.12", "type": "camera", "site": "Farm"},
    "00:1A:2B:3C:50:41": {"name": "FarmCam03", "ip": "10.10.10.13", "type": "camera", "site": "Farm"},
    "00:1A:2B:3C:50:42": {"name": "FarmCam04", "ip": "10.10.10.14", "type": "camera", "site": "Farm"},
    "00:1A:2B:3C:50:43": {"name": "FarmCam05", "ip": "10.10.10.15", "type": "camera", "site": "Farm"},
    "00:1A:2B:3C:50:44": {"name": "FarmCam06", "ip": "10.10.10.16", "type": "camera", "site": "Farm"},
    "00:1A:2B:3C:50:45": {"name": "FarmCam07", "ip": "10.10.10.17", "type": "camera", "site": "Farm"},

    "00:1A:2B:3C:50:46": {"name": "CabinCam01", "ip": "10.10.11.11", "type": "camera", "site": "Cabin"},
    "00:1A:2B:3C:50:47": {"name": "CabinCam02", "ip": "10.10.11.12", "type": "camera", "site": "Cabin"},
    "00:1A:2B:3C:50:48": {"name": "CabinCam03", "ip": "10.10.11.13", "type": "camera", "site": "Cabin"},
    "00:1A:2B:3C:50:49": {"name": "CabinCam04", "ip": "10.10.11.14", "type": "camera", "site": "Cabin"},
    "00:1A:2B:3C:50:4A": {"name": "CabinCam05", "ip": "10.10.11.15", "type": "camera", "site": "Cabin"},
    "00:1A:2B:3C:50:4B": {"name": "CabinCam06", "ip": "10.10.11.16", "type": "camera", "site": "Cabin"},

    "00:1A:2B:3C:50:4C": {"name": "LoftCam01", "ip": "10.10.12.11", "type": "camera", "site": "Loft"},
    "00:1A:2B:3C:50:4D": {"name": "LoftCam02", "ip": "10.10.12.12", "type": "camera", "site": "Loft"},
    "00:1A:2B:3C:50:4E": {"name": "LoftCam03", "ip": "10.10.12.13", "type": "camera", "site": "Loft"},
    "00:1A:2B:3C:50:4F": {"name": "LoftCam04", "ip": "10.10.12.14", "type": "camera", "site": "Loft"},
    "00:1A:2B:3C:50:50": {"name": "LoftCam05", "ip": "10.10.12.15", "type": "camera", "site": "Loft"},
    "00:1A:2B:3C:50:51": {"name": "LoftCam06", "ip": "10.10.12.16", "type": "camera", "site": "Loft"},

    "00:1A:2B:3C:50:52": {"name": "BeachCam01", "ip": "10.10.13.11", "type": "camera", "site": "Beach"},
    "00:1A:2B:3C:50:53": {"name": "BeachCam02", "ip": "10.10.13.12", "type": "camera", "site": "Beach"},
    "00:1A:2B:3C:50:54": {"name": "BeachCam03", "ip": "10.10.13.13", "type": "camera", "site": "Beach"},
    "00:1A:2B:3C:50:55": {"name": "BeachCam04", "ip": "10.10.13.14", "type": "camera", "site": "Beach"},
    "00:1A:2B:3C:50:56": {"name": "BeachCam05", "ip": "10.10.13.15", "type": "camera", "site": "Beach"},
    "00:1A:2B:3C:50:57": {"name": "BeachCam06", "ip": "10.10.13.16", "type": "camera", "site": "Beach"},

    "00:1A:2B:3C:50:58": {"name": "MountainCam01", "ip": "10.10.14.11", "type": "camera", "site": "Mountain"},
    "00:1A:2B:3C:50:59": {"name": "MountainCam02", "ip": "10.10.14.12", "type": "camera", "site": "Mountain"},
    "00:1A:2B:3C:50:5A": {"name": "MountainCam03", "ip": "10.10.14.13", "type": "camera", "site": "Mountain"},
    "00:1A:2B:3C:50:5B": {"name": "MountainCam04", "ip": "10.10.14.14", "type": "camera", "site": "Mountain"},
    "00:1A:2B:3C:50:5C": {"name": "MountainCam05", "ip": "10.10.14.15", "type": "camera", "site": "Mountain"},
    "00:1A:2B:3C:50:5D": {"name": "MountainCam06", "ip": "10.10.14.16", "type": "camera", "site": "Mountain"},

    "00:1A:2B:3C:50:5E": {"name": "DowntownCam01", "ip": "10.10.15.11", "type": "camera", "site": "Downtown"},
    "00:1A:2B:3C:50:5F": {"name": "DowntownCam02", "ip": "10.10.15.12", "type": "camera", "site": "Downtown"},
    "00:1A:2B:3C:50:60": {"name": "DowntownCam03", "ip": "10.10.15.13", "type": "camera", "site": "Downtown"},
    "00:1A:2B:3C:50:61": {"name": "DowntownCam04", "ip": "10.10.15.14", "type": "camera", "site": "Downtown"},
    "00:1A:2B:3C:50:62": {"name": "DowntownCam05", "ip": "10.10.15.15", "type": "camera", "site": "Downtown"},
    "00:1A:2B:3C:50:63": {"name": "DowntownCam06", "ip": "10.10.15.16", "type": "camera", "site": "Downtown"},
    
        # --- Network Switches ---
    "00:1A:2B:4D:20:00": {"name": "OfficeSW1", "ip": "10.10.1.2",  "type": "switch", "site": "Office"},
    "00:1A:2B:4D:20:01": {"name": "OfficeSW2", "ip": "10.10.1.3",  "type": "switch", "site": "Office"},
    "00:1A:2B:4D:20:02": {"name": "LakeSW1",   "ip": "10.10.2.2",  "type": "switch", "site": "Lake House"},
    "00:1A:2B:4D:20:03": {"name": "House1SW1", "ip": "10.10.3.2",  "type": "switch", "site": "House1"},
    "00:1A:2B:4D:20:04": {"name": "House2SW1", "ip": "10.10.4.2",  "type": "switch", "site": "House2"},
    "00:1A:2B:4D:20:05": {"name": "House3SW1", "ip": "10.10.5.2",  "type": "switch", "site": "House3"},
    "00:1A:2B:4D:20:06": {"name": "House4SW1", "ip": "10.10.6.2",  "type": "switch", "site": "House4"},
    "00:1A:2B:4D:20:07": {"name": "House5SW1", "ip": "10.10.7.2",  "type": "switch", "site": "House5"},
    "00:1A:2B:4D:20:08": {"name": "WarehouseSW1", "ip": "10.10.8.2", "type": "switch", "site": "Warehouse"},
    "00:1A:2B:4D:20:09": {"name": "StudioSW1", "ip": "10.10.9.2",  "type": "switch", "site": "Studio"},
    "00:1A:2B:4D:20:0A": {"name": "FarmSW1",   "ip": "10.10.10.2", "type": "switch", "site": "Farm"},
    "00:1A:2B:4D:20:0B": {"name": "CabinSW1",  "ip": "10.10.11.2", "type": "switch", "site": "Cabin"},
    "00:1A:2B:4D:20:0C": {"name": "LoftSW1",   "ip": "10.10.12.2", "type": "switch", "site": "Loft"},
    "00:1A:2B:4D:20:0D": {"name": "BeachSW1",  "ip": "10.10.13.2", "type": "switch", "site": "Beach"},
    "00:1A:2B:4D:20:0E": {"name": "MountainSW1", "ip": "10.10.14.2", "type": "switch", "site": "Mountain"},
    "00:1A:2B:4D:20:0F": {"name": "DowntownSW1", "ip": "10.10.15.2", "type": "switch", "site": "Downtown"},
    "00:1A:2B:4D:20:10": {"name": "HQSW-Core", "ip": "10.10.16.2", "type": "switch", "site": "HQ"},
    "00:1A:2B:4D:20:11": {"name": "HQSW-Edge1", "ip": "10.10.16.3", "type": "switch", "site": "HQ"},
    "00:1A:2B:4D:20:12": {"name": "HQSW-Edge2", "ip": "10.10.16.4", "type": "switch", "site": "HQ"},
    "00:1A:2B:4D:20:13": {"name": "HQSW-Edge3", "ip": "10.10.16.5", "type": "switch", "site": "HQ"},

    # --- Wireless Access Points ---
    "00:1A:2B:4D:30:00": {"name": "OfficeWAP1", "ip": "10.10.1.5", "type": "wap", "site": "Office"},
    "00:1A:2B:4D:30:01": {"name": "OfficeWAP2", "ip": "10.10.1.6", "type": "wap", "site": "Office"},
    "00:1A:2B:4D:30:02": {"name": "LakeWAP1",   "ip": "10.10.2.5", "type": "wap", "site": "Lake House"},
    "00:1A:2B:4D:30:03": {"name": "House1WAP1", "ip": "10.10.3.5", "type": "wap", "site": "House1"},
    "00:1A:2B:4D:30:04": {"name": "House2WAP1", "ip": "10.10.4.5", "type": "wap", "site": "House2"},
    "00:1A:2B:4D:30:05": {"name": "House3WAP1", "ip": "10.10.5.5", "type": "wap", "site": "House3"},
    "00:1A:2B:4D:30:06": {"name": "House4WAP1", "ip": "10.10.6.5", "type": "wap", "site": "House4"},
    "00:1A:2B:4D:30:07": {"name": "House5WAP1", "ip": "10.10.7.5", "type": "wap", "site": "House5"},
    "00:1A:2B:4D:30:08": {"name": "WarehouseWAP1", "ip": "10.10.8.5", "type": "wap", "site": "Warehouse"},
    "00:1A:2B:4D:30:09": {"name": "StudioWAP1", "ip": "10.10.9.5", "type": "wap", "site": "Studio"},
    "00:1A:2B:4D:30:0A": {"name": "FarmWAP1",   "ip": "10.10.10.5", "type": "wap", "site": "Farm"},
    "00:1A:2B:4D:30:0B": {"name": "CabinWAP1",  "ip": "10.10.11.5", "type": "wap", "site": "Cabin"},
    "00:1A:2B:4D:30:0C": {"name": "LoftWAP1",   "ip": "10.10.12.5", "type": "wap", "site": "Loft"},
    "00:1A:2B:4D:30:0D": {"name": "BeachWAP1",  "ip": "10.10.13.5", "type": "wap", "site": "Beach"},
    "00:1A:2B:4D:30:0E": {"name": "MountainWAP1", "ip": "10.10.14.5", "type": "wap", "site": "Mountain"},
    "00:1A:2B:4D:30:0F": {"name": "DowntownWAP1", "ip": "10.10.15.5", "type": "wap", "site": "Downtown"},
    "00:1A:2B:4D:30:10": {"name": "HQWAP-Core", "ip": "10.10.16.5", "type": "wap", "site": "HQ"},
    "00:1A:2B:4D:30:11": {"name": "HQWAP-East", "ip": "10.10.16.6", "type": "wap", "site": "HQ"},
    "00:1A:2B:4D:30:12": {"name": "HQWAP-West", "ip": "10.10.16.7", "type": "wap", "site": "HQ"},
    "00:1A:2B:4D:30:13": {"name": "HQWAP-Guest", "ip": "10.10.16.8", "type": "wap", "site": "HQ"},

}

API_BASE = "http://54.196.221.164:8000"
REGISTER_ENDPOINT = f"{API_BASE}/register"   # one-time snapshot (optional)
STATE_ENDPOINT    = f"{API_BASE}/state"      # transitions + heartbeats
PING_COUNT = "1"
PING_TIMEOUT_SEC = 2
SWEEP_INTERVAL_SEC = 5
DOWN_HEARTBEAT_SEC = 10

# tiny local memory
lastState = {mac: {"status": "unknown", "last_sent_ts": 0.0} for mac in DEVICES}

def now_iso():
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

def is_up(host: str) -> bool:
    sys = platform.system().lower()
    cmd = (["ping", "-n", PING_COUNT, "-w", str(PING_TIMEOUT_SEC * 1000), host]
           if "windows" in sys else
           ["ping", "-c", PING_COUNT, "-W", str(PING_TIMEOUT_SEC), host])
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def post(url, payload):
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def register_once():
    payload = {       
        "reported_at": now_iso(),
        "devices": [{"mac": mac, **info} for mac, info in DEVICES.items()],
    }
    post(REGISTER_ENDPOINT, payload)

def send_event(mac: str, dev: dict, event: str):
    t = now_iso()
    payload = {
        "event": event,              # "down" or "up"
        "occurred_at": t,
        "mac": mac,
        "site": dev["site"],
        "type": dev["type"],
        "name": dev["name"],
        "ip": dev["ip"],
        "idempotency": f'{dev["site"]}:{mac}:{event}:{t}',
    }
    post(STATE_ENDPOINT, payload)
    lastState[mac]["last_sent_ts"] = time.time()

# --- startup (single inventory snapshot) ---
register_once()

# --- main loop ---
while True:
    now_ts = time.time()
    for mac, dev in DEVICES.items():
        status = "up" if is_up(dev["ip"]) else "down"
        prev = lastState[mac]["status"]
        last_sent = lastState[mac]["last_sent_ts"]

        # transitions
        if status != prev:
            send_event(mac, dev, status)   # sends "up" or "down"
        # while DOWN, send periodic heartbeat so API won’t auto-resolve
#        elif status == "down" and (now_ts - last_sent) >= DOWN_HEARTBEAT_SEC:
#            send_event(mac, dev, "down")
#        print(f"sweep tested={len(DEVICES)} elapsed={time.time()-now_ts:.2f}s")
        lastState[mac]["status"] = status

    time.sleep(SWEEP_INTERVAL_SEC)
