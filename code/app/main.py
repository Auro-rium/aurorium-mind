"""FastAPI boundary: authenticates requests, proxies inference, stores safe telemetry."""
from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException, Request

RUST_URL = os.environ.get("RUST_GATEWAY_URL", "http://rust-gateway:9000")
INTERNAL_KEY = os.environ.get("INTERNAL_GATEWAY_KEY", "")
CLIENT_KEY = os.environ.get("CLIENT_API_KEY", "")
TELEMETRY = Path(os.environ.get("TELEMETRY_PATH", "/telemetry/fastapi.jsonl"))
app = FastAPI(title="Aurorium Mind API", version="0.1.0")
telemetry_lock = asyncio.Lock()


async def emit(event: dict[str, Any]) -> None:
    """Persist metadata only. Prompt/completion bodies are deliberately absent."""
    TELEMETRY.parent.mkdir(parents=True, exist_ok=True)
    event["timestamp_ms"] = int(time.time() * 1000)
    async with telemetry_lock:
        with TELEMETRY.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, separators=(",", ":")) + "\n")


def authorize(value: str | None) -> None:
    if CLIENT_KEY and value != f"Bearer {CLIENT_KEY}":
        raise HTTPException(status_code=401, detail="invalid authorization")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "aurorium-mind-api"}


@app.post("/v1/chat/completions")
async def chat(request: Request, authorization: str | None = Header(default=None)) -> Any:
    authorize(authorization)
    request_id = str(uuid.uuid4())
    started = time.perf_counter()
    payload = await request.json()
    messages = payload.get("messages", [])
    if not isinstance(messages, list) or not messages:
        raise HTTPException(status_code=422, detail="messages must be a non-empty list")
    # Only counts are safe telemetry. The actual conversation stays in RAM.
    base_event = {"event": "inference", "request_id": request_id, "message_count": len(messages), "model": payload.get("model", "aurorium")}
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(f"{RUST_URL}/v1/chat/completions", json=payload, headers={"x-request-id": request_id, "x-internal-key": INTERNAL_KEY})
        await emit({**base_event, "status_code": response.status_code, "latency_ms": round((time.perf_counter()-started)*1000, 2)})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        await emit({**base_event, "status_code": 502, "error_class": type(exc).__name__, "latency_ms": round((time.perf_counter()-started)*1000, 2)})
        raise HTTPException(status_code=502, detail="inference upstream unavailable") from exc
