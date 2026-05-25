import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, List

import uvicorn
import orjson  # Rust-based serialization
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import ORJSONResponse 
from pydantic import BaseModel, Field, ValidationError
from groq import AsyncGroq, RateLimitError  

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

# REMOVED DEEPSEEK: Now using high-throughput GPT-OSS 120B reasoning model
MODEL_FALLBACK_CASCADE: List[str] = [
    "gpt-oss-120b",
    "llama-3.3-70b-versatile"
]

# =====================================================================
# 2. CORE INFERENCE LOGIC (Shared Across API & Direct UI Context)
# =====================================================================
async def run_resilient_cascade(client: AsyncGroq, telemetry: Dict[str, Any], anomaly: str) -> Dict[str, Any]:
    system_prompt = (
        "SYSTEM CRITICAL: You are an autonomous industrial hardware controller. "
        "Analyze the provided live telemetry state vectors and execute the required function tool. "
        "Do not output conversational text or pleasantries. Output raw JSON function arguments only."
    )
    
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
            parsed_json = orjson.loads(raw_args)
            
            validated_command = ActuationCommand(**parsed_json)
            return validated_command.model_dump()
            
        except (ValidationError, orjson.JSONDecodeError, RateLimitError, Exception) as schema_err:
            print(f"[FIREWALL INTERCEPT] System shift. Error on {model}: {schema_err}")
            continue

    raise RuntimeError("CRITICAL SHUTDOWN: Entire multi-model fallback loop exhausted.")

# =====================================================================
# 3. HIGH-PERFORMANCE LIFESPAN & FASTAPI INSTANTIATION
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("CRITICAL SHUTDOWN: GROQ_API_KEY environment variable is unassigned.")
    app.state.ai_client = AsyncGroq(api_key=api_key)
    yield  
    await app.state.ai_client.close()

app = FastAPI(title="AETHER-FRACTAL Core Engine", lifespan=lifespan, default_response_class=ORJSONResponse)

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
        return {"status": "SUCCESS", "elapsed_ms": round(processing_ms, 2), "command": command}
    except RuntimeError as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

# =====================================================================
# 4. LOCAL WEB SERVER LAUNCHER GUARD
# =====================================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
