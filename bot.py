import os

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from telegram import Update

from telegram_bot import application

app = FastAPI()


@app.on_event("startup")
async def startup():
    await application.initialize()


@app.on_event("shutdown")
async def shutdown():
    await application.bot.delete_webhook()
    await application.shutdown()


@app.get("/")
async def root():
    return {"message": "TDS Data Analyst Bot Running"}


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/run.jsonl")
async def runlog():
    if os.path.exists("run.jsonl"):
        return FileResponse(
            "run.jsonl",
            media_type="application/json"
        )

    return JSONResponse(
        {"error": "run.jsonl not found"},
        status_code=404,
    )


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    update = Update.de_json(
        data,
        application.bot,
    )

    await application.process_update(update)

    return {"ok": True}