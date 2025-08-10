from api.info import API_KEY, API_MODEL
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re


genai.configure(api_key=API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextPayload(BaseModel):
    text: str

@app.post("/correct")
async def correct_text(payload: TextPayload):
    prompt = f"""
    You are a grammar and spelling correction bot.
    Return ONLY a valid JSON object (no extra text, no explanation) with exactly two keys:
    - corrected: string (the corrected sentence)
    - errors: array of strings (list each error found and the correction made)
    
    Example output:
    {{
        "corrected": "I went to the bank to deposit money at the ATM.",
        "errors": ["go → went", "stick money → deposit money", "retrieval → at the ATM"]
    }}

    Text: "{payload.text}"
    """

    model = genai.GenerativeModel(API_MODEL)
    response = model.generate_content(prompt)

    raw_text = response.text

    # Remove Markdown code fences if present
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[a-zA-Z]*\s*", "", raw_text)  # remove opening fence
        raw_text = re.sub(r"\s*```$", "", raw_text)  # remove closing fence


    print(f"Raw text: {raw_text}")

    try:
        result = json.loads(raw_text)
    except Exception:
        result = {"corrected": "Error parsing response", "errors": []}

    return result
