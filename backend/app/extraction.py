import base64
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_data(file_path: str, content_type: str) -> dict:
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    prompt = """You are an accounting assistant. Extract the following fields from this invoice or receipt image.
    Return ONLY a JSON object with these fields, no extra text:
    {
        "supplier_name": "",
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "description": "",
        "subtotal": "",
        "sales_tax": "",
        "withholding_tax": "",
        "total_amount": "",
        "currency": "",
        "payment_method": ""
    }
    If a field is not found, leave it as empty string."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=content_type),
            prompt
        ]
    )

    raw = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)