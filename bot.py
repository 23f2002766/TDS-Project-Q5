from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()


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