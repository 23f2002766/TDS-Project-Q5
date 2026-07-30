import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Gemini Client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Model Name
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# System Prompt
SYSTEM_PROMPT = """
You are an expert Data Analyst.

Rules:
1. If the user asks a normal question, answer normally.
2. If the question requires calculations, CSV analysis, Excel analysis,
   Python libraries (pandas, numpy, matplotlib), or plotting,
   return ONLY executable Python code inside a markdown code block.
3. Do not include explanations when returning Python code.
4. The code must print the final answer.

If a graph is required:

Save it as

outputs/chart.png

using

plt.savefig("outputs/chart.png")

Do not call plt.show().
"""

def ask_llm(user_message):
    prompt = f"""
{SYSTEM_PROMPT}

User:
{user_message}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text