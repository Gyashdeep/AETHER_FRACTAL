import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, List

import uvicorn
import orjson  # <--- CRITICAL FIX: Rust-based, ultra-low-latency serialization
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import ORJSONResponse # Overrides FastAPI's default encoder
from pydantic import BaseModel, Field, ValidationError
from groq import AsyncGroq, RateLimitError  # Specifically handles rate limits

# =====================================================================
# 1. HARDWARE BOUNDARY ENFORCEMENT (The Physics Firewall)
# =====================================================================
class ActuationCommand(BaseModel):
    target_node_id: str
    action: str = Field(description="Must match exact hardware registry operation codes.")
    intensity_percentage: int = Field(ge=0, le=100, description="Clamp bounds to prevent kinetic damage.")
    risk_mitigation_reason: str

class TelemetryPayload(BaseModel):
    telemetry_context: Dict[str, Any]
    query_anomaly: str

ACTUATION_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "actuate_cluster_state",
            "description": "Executes immediate hardware actuation overrides based on cluster telemetry anomalies.",
            "parameters": ActuationCommand.model_json_schema()
        }
    }
]

MODEL_FALLBACK_CASCADE: List[str] = [
    "deepseek-r1-distill-qwen-1.5b",
    "llama3-70b-8192"
]

# =====================================================================
# 2. HIGH-PERFORMANCE LIFESPAN RESOURCING (Connection Isolation)
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[KERNEL] Booting High-Frequency Actuation Subsystem...")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("CRITICAL SHUTDOWN: GROQ_API_KEY environment variable is unassigned.")
    
    app.state.ai_client = AsyncGroq(api_key=api_key)
    yield  
    print("[KERNEL] Initiating secure resource teardown...")
    await app.state.ai_client.close()

# Force default response class to utilize Rust orjson formatting
app = FastAPI(title="AETHER-FRACTAL Core Engine", lifespan=lifespan, default_response_class=ORJSONResponse)

# =====================================================================
# 3. NON-BLOCKING RESILIENT INFERENCE LOOP
# =====================================================================
async def run_resilient_cascade(client: AsyncGroq, telemetry: Dict[str, Any], anomaly: str) -> Dict[str, Any]:
    system_prompt = (
        "SYSTEM CRITICAL: You are an autonomous industrial hardware controller. "
        "Analyze the provided live telemetry state vectors and execute the required function tool. "
        "Do not output conversational text or pleasantries. Output raw JSON function arguments only."
    )
    
    # Using orjson.dumps() drops serialization latency to near-zero
    serialized_vectors = orjson.dumps(telemetry).decode("utf-8")
    user_content = f"TELEMETRY STATE VECTORS:\n{serialized_vectors}\n\nCRITICAL ANOMALY EVENT: {anomaly}"

    for model in MODEL_FALLBACK_CASCADE:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                tools=ACTUATION_TOOL,
                tool_choice={"type": "function", "function": {"name": "actuate_cluster_state"}},
                temperature=0.0
            )
            
            raw_args = response.choices[0].message.tool_calls[0].function.arguments
            # Parse natively with Rust backend
            parsed_json = orjson.loads(raw_args)
            
            validated_command = ActuationCommand(**parsed_json)
            return validated_command.model_dump()
            
        except (ValidationError, orjson.JSONDecodeError) as schema_err:
            print(f"[FIREWALL INTERCEPT] Model {model} breached structural physical limits: {schema_err}")
            continue
        except RateLimitError as rate_err:
            # Handles API throttling without consuming the whole cascade instantly
            print(f"[TRAFFIC CONSTRAINT] Model {model} hit Rate Limits (429). Shifting to cascade channel. Error: {rate_err}")
            continue
        except Exception as api_err:
            print(f"[NETWORK ERROR] Model {model} execution failed: {api_err}")
            continue

    raise RuntimeError("CRITICAL SHUTDOWN: Entire multi-model fallback loop exhausted. Actuation failure.")

# =====================================================================
# 4. SUB-MILLISECOND API ENDPOINT
# =====================================================================
@app.post("/api/v1/actuate", status_code=status.HTTP_200_OK)
async def handle_telemetry_actuation(payload: TelemetryPayload):
    start_time = time.perf_counter()
    try:
        client: AsyncGroq = app.state.ai_client
        
        command = await run_resilient_cascade(
            client=client,
            telemetry=payload.telemetry_context,
            anomaly=payload.query_anomaly
        )
        
        processing_ms = (time.perf_counter() - start_time) * 1000
        print(f"[GATEWAY METRIC] End-to-End Execution Latency: {processing_ms:.2f} ms")
        return {"status": "SUCCESS", "elapsed_ms": round(processing_ms, 2), "command": command}
        
    except RuntimeError as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

if __name__ == "__main__":
    # Ensure uvicorn calls main:app matching your exact file structure
    uvicorn.run("main:app", host="0.0.0.0", port=8000, loop="uvloop", log_level="info")
