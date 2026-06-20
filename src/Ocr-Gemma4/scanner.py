from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import base64, json, requests
from requests.exceptions import HTTPError, RequestException
from PIL import Image
import io
import os
from pathlib import Path
from PyPDF2 import PdfReader

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - optional dependency
    fitz = None

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
BASE_DIR = Path(__file__).resolve().parent

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_URLS = [
    f"{OLLAMA_BASE_URL}/api/generate",
    "http://localhost:11434/api/generate",
    "http://host.docker.internal:11434/api/generate",
]
OLLAMA_TAGS_URLS = [
    f"{OLLAMA_BASE_URL}/api/tags",
    "http://localhost:11434/api/tags",
    "http://host.docker.internal:11434/api/tags",
]
MODEL = "gemma4:e4b"
SUPPORTED_VISUAL_BUDGETS = {70, 140, 280, 560, 1120}
VISUAL_PROFILE = {
    70: {"max_size": 384, "pdf_scale": 1.25},
    140: {"max_size": 512, "pdf_scale": 1.5},
    280: {"max_size": 768, "pdf_scale": 2.0},
    560: {"max_size": 1024, "pdf_scale": 2.5},
    1120: {"max_size": 1536, "pdf_scale": 3.0},
}

def get_visual_profile(visual_budget: int) -> dict:
    if visual_budget not in SUPPORTED_VISUAL_BUDGETS:
        raise HTTPException(
            status_code=400,
            detail="visual_budget must be one of 70, 140, 280, 560, or 1120.",
        )
    return VISUAL_PROFILE[visual_budget]

def image_to_base64(image_bytes: bytes, max_size: int = 1024) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    if img.mode in ("RGBA", "LA", "P"):
        # JPEG does not support alpha/palette modes, so flatten to RGB first.
        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        rgb_img.paste(img, mask=img.getchannel("A") if "A" in img.getbands() else None)
        img = rgb_img
    elif img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

def extract_or_ocr_pdf(pdf_bytes: bytes, visual_budget: int) -> str:
    profile = get_visual_profile(visual_budget)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    parts = []
    pdf_doc = None
    if fitz is not None:
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    try:
        for page_index, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if text:
                parts.append(text)
                continue

            if pdf_doc is None:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Scanned PDF support requires PyMuPDF (`pip install PyMuPDF`)."
                    ),
                )

            pdf_page = pdf_doc.load_page(page_index)
            pixmap = pdf_page.get_pixmap(
                matrix=fitz.Matrix(profile["pdf_scale"], profile["pdf_scale"]),
                alpha=False,
            )
            page_image_b64 = base64.b64encode(pixmap.tobytes("png")).decode()

            ocr_prompt = """You are a precise OCR engine. Extract ALL text from this PDF page image exactly as it appears.
Preserve line breaks, punctuation, and formatting. Do not interpret or summarize — just extract.
Return ONLY the raw extracted text, nothing else."""

            page_text = call_gemma(ocr_prompt, page_image_b64).strip()
            if page_text:
                parts.append(page_text)
    finally:
        if pdf_doc is not None:
            pdf_doc.close()

    extracted = "\n\n".join(parts).strip()
    if not extracted:
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the PDF.",
        )
    return extracted

def analyze_text(extracted_text: str, target_lang: str) -> dict:
    analysis_prompt = f"""Analyze this text and respond with a JSON object only (no markdown, no backticks):

Text:
{extracted_text}

Respond with this exact JSON structure:
{{
  "detected_language": "the language name in English",
  "script": "the writing system (e.g. Latin, Devanagari, Arabic, CJK)",
  "confidence": "high/medium/low",
  "translation": "full translation into {target_lang}",
  "key_fields": {{"field_name": "value"}}
}}

For key_fields, extract important structured data like names, dates, amounts, addresses if present.
If the text is already in {target_lang}, set translation to the same text."""

    raw = call_gemma_text(analysis_prompt)

    try:
        # Strip any accidental markdown fences
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        analysis = json.loads(clean)
    except json.JSONDecodeError:
        analysis = {
            "detected_language": "unknown",
            "script": "unknown",
            "confidence": "low",
            "translation": raw,
            "key_fields": {}
        }

    return {
        "original_text": extracted_text,
        "detected_language": analysis.get("detected_language"),
        "script": analysis.get("script"),
        "confidence": analysis.get("confidence"),
        "translation": analysis.get("translation"),
        "key_fields": analysis.get("key_fields", {}),
        "target_language": target_lang,
    }

def call_gemma(prompt: str, image_b64: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "options": {"temperature": 0.1}   # low temp = more faithful OCR
    }
    last_exc = None
    for ollama_url in OLLAMA_URLS:
        try:
            r = requests.post(ollama_url, json=payload, timeout=60)
            r.raise_for_status()
            break
        except HTTPError as exc:
            response_text = exc.response.text if exc.response is not None else ""
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Ollama returned an error from {ollama_url}: "
                    f"{response_text or str(exc)}"
                ),
            ) from exc
        except RequestException as exc:
            last_exc = exc
    else:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Cannot reach Ollama at {OLLAMA_URLS[0]} or {OLLAMA_URLS[1]}. "
                "Start it with `ollama serve` and make sure the model "
                f"`{MODEL}` is available."
            ),
        ) from last_exc

    try:
        return r.json()["response"]
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned an unexpected response from {ollama_url}.",
        ) from exc

def call_gemma_text(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    last_exc = None
    for ollama_url in OLLAMA_URLS:
        try:
            r = requests.post(ollama_url, json=payload, timeout=60)
            r.raise_for_status()
            break
        except HTTPError as exc:
            response_text = exc.response.text if exc.response is not None else ""
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Ollama returned an error from {ollama_url}: "
                    f"{response_text or str(exc)}"
                ),
            ) from exc
        except RequestException as exc:
            last_exc = exc
    else:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Cannot reach Ollama at {OLLAMA_URLS[0]} or {OLLAMA_URLS[1]}. "
                "Start it with `ollama serve` and make sure the model "
                f"`{MODEL}` is available."
            ),
        ) from last_exc

    try:
        return r.json()["response"]
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned an unexpected response from {ollama_url}.",
        ) from exc

def probe_ollama() -> dict:
    last_exc = None
    for tags_url in OLLAMA_TAGS_URLS:
        try:
            r = requests.get(tags_url, timeout=10)
            r.raise_for_status()
            payload = r.json()
            models = payload.get("models", [])
            model_names = [
                item.get("name")
                for item in models
                if isinstance(item, dict) and item.get("name")
            ]
            return {
                "reachable": True,
                "endpoint": tags_url,
                "model": MODEL,
                "model_available": MODEL in model_names,
                "models": model_names,
            }
        except RequestException as exc:
            last_exc = exc
        except ValueError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama returned invalid JSON from {tags_url}.",
            ) from exc

    raise HTTPException(
        status_code=503,
        detail=(
            f"Cannot reach Ollama at {OLLAMA_TAGS_URLS[0]} or {OLLAMA_TAGS_URLS[1]}. "
            "Start it with `ollama serve` and make sure the server is available."
        ),
    ) from last_exc

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/ollama")
async def health_ollama():
    return probe_ollama()

@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "index.html")

@app.post("/scan")
async def scan_document(
    file: UploadFile = File(...),
    target_lang: str = Form(default="English"),
    visual_budget: int = Form(default=560),
):
    image_bytes = await file.read()
    ext = Path(file.filename or "").suffix.lower()
    profile = get_visual_profile(visual_budget)

    if ext == ".pdf" or file.content_type == "application/pdf":
        extracted_text = extract_or_ocr_pdf(image_bytes, visual_budget)
        return analyze_text(extracted_text, target_lang)

    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image and PDF files are supported.",
        )

    image_b64 = image_to_base64(image_bytes, max_size=profile["max_size"])

    ocr_prompt = """You are a precise OCR engine. Extract ALL text from this document image exactly as it appears.
Preserve line breaks, punctuation, and formatting. Do not interpret or summarize — just extract.
Return ONLY the raw extracted text, nothing else."""

    extracted_text = call_gemma(ocr_prompt, image_b64)

    return analyze_text(extracted_text, target_lang)

# Run with:
#   uvicorn --app-dir src/Ocr-Gemma4 scanner:app --reload
# or from inside src/Ocr-Gemma4:
#   uvicorn scanner:app --reload
