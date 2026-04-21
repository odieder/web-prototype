import logging
import json
import re
from datetime import date
from io import BytesIO
from tempfile import NamedTemporaryFile

import pytesseract
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from PIL import Image, UnidentifiedImageError

app = FastAPI()
client = OpenAI()
logger = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff",
    "application/pdf",
}
CATEGORY_LIST = ("Rundfunk", "Krankenkasse", "Finanzamt", "Mahnung", "Miete", "Sonstiges")
URGENCY_LEVELS = {"low", "medium", "high"}
OPENAI_MODEL = "gpt-4.1-mini"


def extract_text(content: bytes, content_type: str) -> str:
    try:
        if content_type == "application/pdf":
            with NamedTemporaryFile(suffix=".pdf") as temp_pdf:
                temp_pdf.write(content)
                temp_pdf.flush()
                return pytesseract.image_to_string(temp_pdf.name).strip()

        image = Image.open(BytesIO(content))
        return pytesseract.image_to_string(image).strip()
    except (UnidentifiedImageError, OSError, RuntimeError, pytesseract.TesseractError) as exc:
        raise HTTPException(status_code=422, detail="OCR failed for the uploaded file") from exc


def _extract_response_text(response) -> str:
    text = (getattr(response, "output_text", None) or "").strip()
    if text:
        return text

    for item in getattr(response, "output", []) or []:
        content_items = getattr(item, "content", []) or []
        for content in content_items:
            candidate = (getattr(content, "text", None) or "").strip()
            if candidate:
                return candidate
    return ""


def _extract_json_object(raw: str) -> str:
    text = raw.strip()
    if text.startswith("{") and text.endswith("}"):
        return text

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _normalize_category(value: str) -> str:
    normalized = (value or "").strip()
    category_map = {
        "rundfunk": "Rundfunk",
        "krankenkasse": "Krankenkasse",
        "finanzamt": "Finanzamt",
        "mahnung": "Mahnung",
        "miete": "Miete",
        "sonstiges": "Sonstiges",
    }
    category = category_map.get(normalized.lower(), "Sonstiges")
    return category if category in CATEGORY_LIST else "Sonstiges"


def _parse_relative_deadline_text(text: str):
    patterns = [
        re.compile(
            r"\b(?:innerhalb von|binnen|in)\s+(\d{1,3})\s+(tag|tagen|tage|woche|wochen|monat|monaten|monate)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bfrist(?:\s+von)?\s+(\d{1,3})\s+(tag|tagen|tage|woche|wochen|monat|monaten|monate)\b",
            re.IGNORECASE,
        ),
    ]
    for pattern in patterns:
        match = pattern.search(text)
        if not match:
            continue
        amount = int(match.group(1))
        unit = match.group(2).lower()
        if unit.startswith("tag"):
            return f"P{amount}D", match.group(0)
        if unit.startswith("woche"):
            return f"P{amount}W", match.group(0)
        if unit.startswith("monat"):
            return f"P{amount}M", match.group(0)
    return None, None


def _find_deadline_with_regex(text: str):
    absolute_pattern = re.compile(r"\b([0-3]?\d)[\./-]([01]?\d)[\./-]((?:20)?\d{2})\b")
    for match in absolute_pattern.finditer(text):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        if year < 100:
            year += 2000
        try:
            return date(year, month, day).isoformat(), match.group(0)
        except ValueError:
            continue

    return _parse_relative_deadline_text(text)


def _parse_ai_payload(raw: str):
    if not raw:
        raise HTTPException(status_code=502, detail="Empty AI response")

    json_blob = _extract_json_object(raw)
    try:
        payload = json.loads(json_blob)
    except json.JSONDecodeError as exc:
        logger.error("analyze_document: invalid JSON from model raw=%r", raw)
        raise HTTPException(status_code=502, detail="Invalid JSON from AI") from exc

    summary = str(payload.get("summary") or "").strip()
    action = str(payload.get("action") or "").strip()
    if not summary or not action:
        raise HTTPException(status_code=502, detail="Incomplete AI response")

    urgency = str(payload.get("urgency") or "").strip().lower()
    if urgency not in URGENCY_LEVELS:
        urgency = "medium"

    deadline = payload.get("deadline")
    deadline_text = payload.get("deadline_text")

    return {
        "category": _normalize_category(str(payload.get("category") or "")),
        "summary": summary,
        "action": action,
        "deadline": deadline if isinstance(deadline, str) and deadline.strip() else None,
        "deadline_text": (
            deadline_text if isinstance(deadline_text, str) and deadline_text.strip() else None
        ),
        "urgency": urgency,
    }


def analyze_document(text: str):
    logger.info("analyze_document: start (chars=%d, model=%s)", len(text), OPENAI_MODEL)
    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=(
                "Du analysierst deutsche Behördenbriefe. "
                "Antworte AUSSCHLIESSLICH als valides JSON ohne Markdown oder Zusatztext.\n\n"
                "Nutze genau dieses Schema:\n"
                "{\n"
                '  "category": string,\n'
                '  "summary": string,\n'
                '  "action": string,\n'
                '  "deadline": string | null,\n'
                '  "deadline_text": string | null,\n'
                '  "urgency": "low" | "medium" | "high"\n'
                "}\n\n"
                "Regeln:\n"
                "- Sprache: Deutsch für summary/action.\n"
                f"- category muss genau eine davon sein: {', '.join(CATEGORY_LIST)}.\n"
                "- Extrahiere Fristen explizit:\n"
                "  - absolute Daten (z. B. 12.03.2026)\n"
                "  - relative Fristen (z. B. innerhalb von 14 Tagen)\n"
                "- deadline enthält den normalisierten Wert (Datum oder relative Frist), deadline_text die Original-Textstelle.\n"
                "- Wenn keine Frist erkennbar ist: deadline = null und deadline_text = null.\n\n"
                f"Dokumenttext:\n{text[:6000]}"
            ),
            max_output_tokens=350,
        )
    except Exception as exc:
        logger.exception("analyze_document: OpenAI request failed")
        raise HTTPException(status_code=502, detail="AI analysis failed") from exc

    raw = _extract_response_text(response)
    result = _parse_ai_payload(raw)

    # 2nd layer: regex fallback for missed deadlines.
    if not result["deadline"]:
        regex_deadline, regex_text = _find_deadline_with_regex(text)
        if regex_deadline:
            result["deadline"] = regex_deadline
            result["deadline_text"] = regex_text
    return result


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Upload an image or PDF.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    text = extract_text(content=content, content_type=file.content_type)
    if not text.strip():
        raise HTTPException(status_code=422, detail="No readable text found in document.")

    analysis = analyze_document(text=text)

    return {
        "filename": file.filename,
        "category": analysis["category"],
        "summary": analysis["summary"],
        "action": analysis["action"],
        "deadline": analysis["deadline"],
        "deadline_text": analysis["deadline_text"],
        "urgency": analysis["urgency"],
    }
