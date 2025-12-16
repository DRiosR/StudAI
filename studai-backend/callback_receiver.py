"""Minimal FastAPI app that receives POST updates from the pipeline and prints/logs them.

Run:
  pip install fastapi uvicorn
  uvicorn callback_receiver:app --host 0.0.0.0 --port 9000

Endpoints:
  POST /callback  - accepts JSON payloads from pipeline and prints them
"""
from fastapi import FastAPI, Request
import asyncio

app = FastAPI()

@app.post("/callback")
async def receive_callback(request: Request):
    data = await request.json()
    # You can add more complex logic here (store to DB, forward to clients, etc.)
    print("Received callback:", data)
    return {"status": "ok"}
