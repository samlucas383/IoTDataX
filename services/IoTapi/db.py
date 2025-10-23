# app.py
import os, json, asyncio
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, field_validator
import asyncpg

PG_DSN = os.getenv("DATABASE_URL", "postgresql://iotuser:iotpass@postgres:5432/iotdb")
BATCH_SIZE = int(os.getenv("INGEST_BATCH", "500"))
BATCH_WAIT_MS = int(os.getenv("INGEST_BATCH_WAIT_MS", "20"))

app = FastAPI(title="Universal Ingest")

class Ingest(BaseModel):
    app_id: str
    ts: int                       # epoch ms
    payload: Dict[str, Any]
    device_id: Optional[str] = None
    msg_id: Optional[str] = None
    topic: Optional[str] = None

    @field_validator("ts")
    @classmethod
    def _positive_ts(cls, v: int):
        if v <= 0: raise ValueError("ts must be epoch ms > 0")
        return v

queue: "asyncio.Queue[Ingest]" = asyncio.Queue()
pool: asyncpg.Pool

INSERT_SQL = """
INSERT INTO telemetry_raw (app_id, device_id, ts, msg_id, topic, body)
VALUES ($1,$2,$3,$4,$5,$6::jsonb)
ON CONFLICT (app_id, msg_id) DO NOTHING
"""

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(PG_DSN, min_size=1, max_size=10)
    # background worker
    asyncio.create_task(_writer())

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

@app.post("/ingest")
async def ingest(body: Ingest):
    try:
        queue.put_nowait(body)
    except asyncio.QueueFull:
        raise HTTPException(503, "ingest backpressure")
    return {"status": "queued"}

async def _writer():
    """Batch rows for efficient inserts."""
    conn: Optional[asyncpg.Connection] = None
    try:
        while True:
            batch = []
            try:
                item = await asyncio.wait_for(queue.get(), timeout=BATCH_WAIT_MS/1000)
                batch.append(item)
            except asyncio.TimeoutError:
                pass

            while len(batch) < BATCH_SIZE:
                try:
                    batch.append(queue.get_nowait())
                except asyncio.QueueEmpty:
                    break

            if not batch:
                continue

            if conn is None:
                conn = await pool.acquire()

            async with conn.transaction():
                await conn.executemany(
                    INSERT_SQL,
                    [(b.app_id, b.device_id, b.ts, b.msg_id, b.topic, json.dumps(b.payload)) for b in batch],
                )
    except asyncio.CancelledError:
        pass
    finally:
        if conn:
            await pool.release(conn)
