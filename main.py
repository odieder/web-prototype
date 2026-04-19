import logging
from io import BytesIO
from tempfile import NamedTemporaryFile

import pytesseract
from fastapi import FastAPI, File, HTTPException, UploadFile
from openai import OpenAI
from PIL import Image, UnidentifiedImageError

app = FastAPI()
client = OpenAI()
logger = logging.getLogger("uvicorn.error")


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
CATEGORIES = {"Rechnung", "Amt", "Vertrag", "Spam", "Einladung"}
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


def classify_text(text: str) -> str:
    logger.info("classify_text: start (chars=%d, model=%s)", len(text), OPENAI_MODEL)
    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=(
                "Classify this document text into exactly one label: "
                "Rechnung, Amt, Vertrag, Spam, Einladung.  Return only the label.\n\n"
                f"Text:\n{text[:4000]}"
            ),
            max_output_tokens=32,
        )
    except Exception as exc:
        logger.exception("classify_text: OpenAI request failed")
        raise HTTPException(status_code=502, detail="Text classification failed") from exc

    raw = _extract_response_text(response)
    normalized = raw.strip().strip('"').strip("'").splitlines()[0].strip() if raw else ""

    for category in CATEGORIES:
        if normalized.lower() == category.lower():
            logger.info("classify_text: resolved category=%s", category)
            return category

    for category in CATEGORIES:
        if category.lower() in normalized.lower():
            logger.info("classify_text: resolved fuzzy category=%s from raw=%r", category, raw)
            return category

    logger.error("classify_text: invalid model output raw=%r", raw)
    if not normalized:
        raise HTTPException(status_code=502, detail="Empty classification response")
    if normalized not in CATEGORIES:
        raise HTTPException(status_code=502, detail="Invalid classification response")
    return normalized


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Upload an image or PDF.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    text = extract_text(content=content, content_type=file.content_type)
    category = classify_text(text)
    return {"filename": file.filename, "text": text, "category": category}
