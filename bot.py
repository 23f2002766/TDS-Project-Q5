from fastapi.responses import FileResponse
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
from telegram_bot import main as telegram_main

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Telegram bot in background
    threading.Thread(target=telegram_main, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {
        "message": "TDS Data Analyst Bot Running"
    }

@app.get("/health")
def health():
    return {
        "ok": True
    }


@app.get("/run.jsonl")
def get_log():
    if os.path.exists("run.jsonl"):
        return FileResponse(
            "run.jsonl",
            media_type="application/json"
        )

    return {
        "error": "run.jsonl not found"
    }