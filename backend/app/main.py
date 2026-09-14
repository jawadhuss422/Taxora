from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from app.extraction import extract_invoice_data

app = FastAPI(
    title="Taxora API",
    description="AI-powered bookkeeping and tax-preparation platform for Pakistani businesses",
    version="0.1.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Taxora API is running", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF, JPG and PNG files are allowed"}
        )
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "status": "uploaded"
    }

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"error": "Only JPG and PNG files are supported for extraction currently"}
        )
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extracted = extract_invoice_data(file_path, file.content_type)
    return {
        "message": "Extraction complete",
        "filename": file.filename,
        "extracted_data": extracted
    }