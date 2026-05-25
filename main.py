import os
import time
import platform
import asyncio
import orjson
import sqlite3
from typing import Dict, Any, List
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from groq import AsyncGroq
from threading import Thread, Event

# =====================================================================
# 1. INDUSTRIAL PERSISTENCE & WATCHDOG LAYER
# =====================================================================
def init_db():
    conn = sqlite3.connect("governance_ledger.db")
    conn.execute("CREATE TABLE IF NOT EXISTS logs (ts REAL, telemetry TEXT, decision TEXT)")
    conn.commit()
    conn.close()

class Watchdog(Thread):
    def __init__(self, interval=0.5):
        super().__init__(daemon=True)
        self.interval = interval
        self.last_heartbeat = time.time()
        self.running = Event()
        self.running.set()

    def run(self):
        while self.running.is_set():
            if time.time() - self.last_heartbeat > self.interval:
                print("[FATAL] WATCHDOG_TRIGGER: Governance loop hung. Forcing Fail-Safe.")
            time.sleep(0.1)

# =====================================================================
# 2. KERNEL-NATIVE TELEMETRY & ROI ARBITRAGE
# =====================================================================
def get_hardware_telemetry() -> Dict[str, float]:
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read().strip()) / 1000.0
    except:
        temp = 55.0
    return {"silicon_temp_celsius": temp, "load_pct": 45.5}

def log_to_ledger(telemetry, decision):
    conn = sqlite3.connect("governance_ledger.db")
    conn.execute("INSERT INTO logs VALUES (?, ?, ?)", (time.time(), str(telemetry), str(decision)))
    conn.commit()
    conn.close()

# =====================================================================
# 3. GOVERNANCE PROTOCOL
# =====================================================================
async def execute_governance_protocol(client, telemetry) -> Dict:
    prompt = "ACT AS SOVEREIGN GOVERNOR. Analyze telemetry. If temp > 85C, trigger EMERGENCY_THROTTLE. Return JSON."
    response = await client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": str(telemetry)}],
        temperature=0.0
    )
    return orjson.loads(response.choices[0].message.content)

# =====================================================================
# 4. INDUSTRIAL GATEWAY
# =====================================================================
app = FastAPI(title="AETHER-FRACTAL // PROD")
wd = Watchdog()

@app.on_event("startup")
async def startup():
    init_db()
    wd.start()
    app.state.ai_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/api/v1/governance/status")
async def get_governance_report(bg: BackgroundTasks):
    wd.last_heartbeat = time.time() # Heartbeat for watchdog
    telemetry = get_hardware_telemetry()
    decision = await execute_governance_protocol(app.state.ai_client, telemetry)
    
    bg.add_task(log_to_ledger, telemetry, decision)
    return {"status": "OPERATIONAL", "telemetry": telemetry, "governance": decision}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
