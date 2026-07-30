import asyncio
from executor import run_python
from memory import (
    add_message,
    get_history,
    set_last_file,
    get_last_file,
)
import json
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from llm import ask_llm
from logger import write_log

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Hello! TDS Data Analyst Bot is running."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    # Log user message
    write_log(
        "user_message",
        {
            "chat_id": chat_id,
            "text": user_message
        }
    )

    # Save user message
    add_message(chat_id, "user", user_message)

    # Conversation history
    history = get_history(chat_id)

    # Last uploaded file
    last_file = get_last_file(chat_id)
    

    file_type = None

    if last_file:
       _, ext = os.path.splitext(last_file)
    file_type = ext.lower()


    # ---------------------------
    # Build Prompt
    # ---------------------------
    prompt = """
You are an expert AI Data Analyst.

Rules:

1. Answer normal questions normally.

2. If the user asks about an uploaded CSV or Excel file,
   return ONLY executable Python code.

3. Always use pandas.

4. The code must print the final answer.

5. Do not explain the code.

"""

    if last_file:
        prompt += f"""
The user has uploaded this file:

{last_file}

File Type:

{file_type}

Rules:

- If file type is .csv use pandas.read_csv()

- If file type is .xlsx or .xls use pandas.read_excel()

Always read THIS exact file.
"""

    prompt += "\nConversation:\n"

    for msg in history:
        prompt += f"{msg['role']}: {msg['content']}\n"

    try:
        ai_response = ask_llm(prompt)

        # If Gemini returned Python code
        if ai_response.strip().startswith("```python"):

            code = (
                ai_response
                .replace("```python", "")
                .replace("```", "")
                .strip()
            )

            print("\n===== PYTHON CODE GENERATED =====")
            print(code)
            print("=================================\n")

            # Execute Python
            ai_response = run_python(code)

            if os.path.exists("outputs/chart.png"):
                await update.message.reply_photo(
                  photo=open("outputs/chart.png", "rb")
            )

    except Exception as e:
        print(e)

    ai_response = (
        "Sorry, I couldn't complete the analysis.\n"
        f"{str(e)}"
    )
    
    # Save assistant reply
    add_message(chat_id, "assistant", ai_response)

    # Log bot reply
    write_log(
        "bot_reply",
        {
            "chat_id": chat_id,
            "text": ai_response
        }
    )

    response = {
        "answer": ai_response,
        "log_url": f"{BASE_URL}/run.jsonl"
    }

    await update.message.reply_text(
        json.dumps(response, indent=2)
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    file = await context.bot.get_file(document.file_id)

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", document.file_name)

    await file.download_to_drive(file_path)

    set_last_file(update.effective_chat.id, file_path)

    write_log(
        "document_uploaded",
        {
            "chat_id": update.effective_chat.id,
            "filename": document.file_name
        }
    )

    response = {
        "answer": f"File uploaded.\nSaved Path:\n{file_path}",
        "log_url": "http://127.0.0.1:8000/run.jsonl"
    }

    await update.message.reply_text(
        json.dumps(response, indent=2)
    )


def main():
    asyncio.run(start_bot())


async def start_bot():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            echo
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            handle_document
        )
    )

    print("✅ Telegram Bot Started...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    main()