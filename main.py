from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from PIL import Image
import pytesseract
import os
import io
import fitz  # PyMuPDF for PDF
from asosoft.corrector import correct_kurdish_text  # ← this is custom

app = FastAPI()

# Allow React frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file: bytes) -> str:
    text = ""
    with fitz.open(stream=file, filetype="pdf") as pdf:
        for page in pdf:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            text += pytesseract.image_to_string(image, lang="ckb+eng+ara")
    return text

@app.post("/ocr")
async def ocr_api(file: UploadFile = File(...), lang: Optional[str] = Form("ckb")):
    ext = file.filename.lower().split('.')[-1]
    content = await file.read()
    try:
        if ext == "pdf":
            text = extract_text_from_pdf(content)
        else:
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image, lang="ckb+eng+ara")
        
        # AsoSoft correction (Kurdish only)
        if "ckb" in lang:
            text = correct_kurdish_text(text)

        return { "text": text.strip() }

    except Exception as e:
        return { "text": f"Error processing file: {str(e)}" }
