from fastapi import FastAPI, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, UTC
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(sweeper())
    print("Sweeper started")
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Sweeper stopped")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:54445",
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STALE_SEC = 180
SWEEP_SEC = 30

STATE: Dict[str, Dict[str, Any]] = {}
IDEMPOTENCY: set[str] = set()

def now_utc() -> datetime:
    return datetime.now(UTC)

def parse_iso_utc(s: Optional[str]) -> datetime:
    if not s:
        return now_utc()
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return dt.astimezone(UTC) if dt.tzinfo else dt.replace(tzinfo=UTC)

def iso_z(dt_: Optional[datetime]) -> Optional[str]:
    if not dt_:
        return None
    return dt_.astimezone(UTC).isoformat().replace("+00:00", "Z")

def ensure_record(mac: str) -> Dict[str, Any]:
    rec = STATE.get(mac)
    if rec is None:
        rec = {
            "mac": mac,
            "site": None,
            "type": None,
            "name": None,
            "ip": None,
            "status": "up",
            "first_down_at": None,
            "last_seen": None,
            "last_change_at": None,          # NEW
            "last_failure_reason": None,     # NEW
            "latency_ms": None,              # NEW (latest observed)
            "metrics": {
                "incidents_total": 0,
                "total_downtime_sec": 0.0,
                "failure_count": 0,          # NEW (resets on up)
            },
            "history": []
        }
        STATE[mac] = rec
    return rec

def serialize_state() -> Dict[str, Any]:
    out = {}
    for mac, rec in STATE.items():
        out[mac] = {
            "mac": rec["mac"],
            "site": rec.get("site"),
            "type": rec.get("type"),
            "name": rec.get("name"),
            "ip": rec.get("ip"),
            "status": rec.get("status"),
            "first_down_at": iso_z(rec.get("first_down_at")),
            "last_seen": iso_z(rec.get("last_seen")),
            "last_change_at": iso_z(rec.get("last_change_at")),      # NEW
            "last_failure_reason": rec.get("last_failure_reason"),   # NEW
            "latency_ms": rec.get("latency_ms"),                     # NEW
            "metrics": rec.get("metrics", {}),
            "history": rec.get("history", []),
        }
    return out

@app.post("/register")
async def register(payload: Dict[str, Any]):
    site = payload.get("site")
    devices = payload.get("devices", []) or []
    for d in devices:
        mac = d.get("mac")
        if not mac:
            continue
        rec = ensure_record(mac)
        rec["site"] = d.get("site") or site or rec.get("site")
        rec["type"] = d.get("type") or rec.get("type")
        rec["name"] = d.get("name") or rec.get("name")
        rec["ip"]   = d.get("ip")   or rec.get("ip")
    return {"ok": True, "state": serialize_state()}

@app.post("/state")
async def post_state(state: Dict[str, Any]):
    """
    From site agent:
    {
      "event": "down" | "up",
      "occurred_at": "2025-10-11T15:20:00Z",
      "mac": "...",
      "site": "LanBra",
      "type": "camera",
      "name": "FrontCam",
      "ip": "10.10.1.47",
      "reason": "timeout|dns|http_5xx|...",     # NEW optional
      "latency_ms": 123.4,                      # NEW optional
      "idempotency": "site:mac:event:ts"
    }
    """
    idem = state.get("idempotency")
    if idem and idem in IDEMPOTENCY:
        return {"ok": True, "state": serialize_state()}
    if idem:
        IDEMPOTENCY.add(idem)

    mac = state.get("mac")
    if not mac:
        return {"ok": False, "error": "missing mac"}

    event = (state.get("event") or "").lower()
    occurred_dt = parse_iso_utc(state.get("occurred_at"))
    rec = ensure_record(mac)

    # keep inventory fresh
    rec["site"] = state.get("site") or rec.get("site")
    rec["type"] = state.get("type") or rec.get("type")
    rec["name"] = state.get("name") or rec.get("name")
    rec["ip"]   = state.get("ip")   or rec.get("ip")

    # Optional telemetry
    incoming_reason = state.get("reason")
    incoming_latency = state.get("latency_ms")

    if event == "down" or event == "unknown":
        if rec["status"] != "down":
            # opening new incident
            rec["status"] = "down"
            rec["first_down_at"] = occurred_dt
            rec["last_seen"] = occurred_dt
            rec["last_change_at"] = occurred_dt          # NEW
            rec["metrics"]["failure_count"] += 1         # NEW
            if incoming_reason:
                rec["last_failure_reason"] = incoming_reason  # NEW
        else:
            # heartbeat extends last_seen
            rec["last_seen"] = max(rec["last_seen"], occurred_dt) if rec["last_seen"] else occurred_dt
            # update reason/latency if provided on heartbeats
            if incoming_reason:
                rec["last_failure_reason"] = incoming_reason
        # update last observed latency if provided
        if isinstance(incoming_latency, (int, float)):
            rec["latency_ms"] = float(incoming_latency)

    elif event == "up":
        if rec["status"] == "down":
            start = rec["first_down_at"] or occurred_dt
            end = occurred_dt
            duration = max(0.0, (end - start).total_seconds())
            rec["metrics"]["incidents_total"] += 1
            rec["metrics"]["total_downtime_sec"] += duration
            rec["history"].append({
                "start": iso_z(start),
                "end": iso_z(end),
                "duration_sec": round(duration, 3)
            })
        # flip to up; reset/transitions
        rec["status"] = "up"
        rec["first_down_at"] = None
        rec["last_seen"] = None
        rec["last_change_at"] = occurred_dt              # NEW
        rec["metrics"]["failure_count"] = 0              # NEW (reset)
        rec["latency_ms"] = None                         # NEW (no current latency)
        # keep last_failure_reason for post-mortem; clear if you prefer:
        # rec["last_failure_reason"] = None

    else:
        return {"ok": False, "error": "invalid event"}

    return {"ok": True, "state": serialize_state()}

@app.get("/state")
async def get_state():
    return {"ok": True, "state": serialize_state()}

async def sweeper():
    while True:
        await asyncio.sleep(SWEEP_SEC)
        now = now_utc()
        for rec in STATE.values():
            if rec["status"] == "down" and rec["last_seen"]:
                if (now - rec["last_seen"]) > timedelta(seconds=STALE_SEC):
                    start = rec["first_down_at"] or rec["last_seen"]
                    end = rec["last_seen"] + timedelta(seconds=STALE_SEC)
                    duration = max(0.0, (end - start).total_seconds())
                    rec["metrics"]["incidents_total"] += 1
                    rec["metrics"]["total_downtime_sec"] += duration
                    rec["history"].append({
                        "start": iso_z(start),
                        "end": iso_z(end),
                        "duration_sec": round(duration, 3),
                    })
                    rec["status"] = "up"
                    rec["first_down_at"] = None
                    rec["last_seen"] = None
                    rec["last_change_at"] = end            # NEW
                    rec["metrics"]["failure_count"] = 0    # NEW
                    rec["latency_ms"] = None               # NEW

@app.get("/health")
async def health():
    return {"ok": True, "ts": iso_z(now_utc())}

@app.get("/summary")
async def summary():
    total = len(STATE)
    by_status = {"up": 0, "down": 0, "unknown": 0}
    by_site, by_type = {}, {}
    for rec in STATE.values():
        st = rec.get("status") or "unknown"
        by_status[st] = by_status.get(st, 0) + 1
        site = rec.get("site") or "unknown"
        typ  = rec.get("type") or "unknown"
        by_site[site] = by_site.get(site, 0) + 1
        by_type[typ]  = by_type.get(typ, 0) + 1
    return {"ok": True, "total": total, "by_status": by_status, "by_site": by_site, "by_type": by_type}

@app.get("/devices")
async def list_devices(
    site: str | None = None,
    type: str | None = Query(None, alias="type"),
    status: str | None = None,
    limit: int = 500,
    offset: int = 0,
):
    rows: List[dict] = []
    for mac, rec in STATE.items():
        if site   and (rec.get("site")  != site):   continue
        if type   and (rec.get("type")  != type):   continue
        if status and (rec.get("status")!= status): continue
        rows.append({
            "mac": mac,
            "site": rec.get("site"),
            "type": rec.get("type"),
            "name": rec.get("name"),
            "ip": rec.get("ip"),
            "status": rec.get("status"),
            "first_down_at": iso_z(rec.get("first_down_at")),
            "last_seen": iso_z(rec.get("last_seen")),
            "last_change_at": iso_z(rec.get("last_change_at")),      # NEW
            "last_failure_reason": rec.get("last_failure_reason"),   # NEW
            "latency_ms": rec.get("latency_ms"),                     # NEW
            "metrics": rec.get("metrics", {}),
        })
    return {"ok": True, "items": rows[offset:offset+limit], "total": len(rows)}

@app.get("/devices/{mac}")
async def get_device(mac: str):
    rec = STATE.get(mac)
    if not rec:
        return {"ok": False, "error": "not found"}
    return {
        "ok": True,
        "device": {
            "mac": mac,
            "site": rec.get("site"),
            "type": rec.get("type"),
            "name": rec.get("name"),
            "ip": rec.get("ip"),
            "status": rec.get("status"),
            "first_down_at": iso_z(rec.get("first_down_at")),
            "last_seen": iso_z(rec.get("last_seen")),
            "last_change_at": iso_z(rec.get("last_change_at")),      # NEW
            "last_failure_reason": rec.get("last_failure_reason"),   # NEW
            "latency_ms": rec.get("latency_ms"),                     # NEW
            "metrics": rec.get("metrics", {}),
            "history": rec.get("history", []),
        }
    }

@app.get("/incidents/open")
async def incidents_open(site: str | None = None, type: str | None = Query(None, alias="type")):
    items = []
    for mac, rec in STATE.items():
        if rec.get("status") != "down":
            continue
        if site and rec.get("site") != site:
            continue
        if type and rec.get("type") != type:
            continue
        items.append({
            "mac": mac,
            "site": rec.get("site"),
            "type": rec.get("type"),
            "name": rec.get("name"),
            "ip": rec.get("ip"),
            "start": iso_z(rec.get("first_down_at")),
            "last_seen": iso_z(rec.get("last_seen")),
            "last_failure_reason": rec.get("last_failure_reason"),   # NEW
            "latency_ms": rec.get("latency_ms"),                     # NEW
        })
    return {"ok": True, "items": items, "total": len(items)}

@app.get("/incidents/history")
async def incidents_history(
    site: str | None = None,
    mac: str | None = None,
    since: str | None = None,
    limit: int = 500,
    offset: int = 0,
):
    since_dt: datetime | None = parse_iso_utc(since) if since else None
    rows = []
    for m, rec in STATE.items():
        if mac and m != mac: continue
        if site and rec.get("site") != site: continue
        for h in rec.get("history", []):
            if since_dt and parse_iso_utc(h["end"]) < since_dt:
                continue
            rows.append({
                "mac": m,
                "site": rec.get("site"),
                "type": rec.get("type"),
                "name": rec.get("name"),
                "ip": rec.get("ip"),
                **h
            })
    rows.sort(key=lambda r: r.get("end") or r.get("start"), reverse=True)
    return {"ok": True, "items": rows[offset:offset+limit], "total": len(rows)}
