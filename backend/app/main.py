from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from app.extraction import extract_invoice_data
from app.export import export_to_excel
from app.tax_engine import process_invoice_tax

app = FastAPI(
    title="Taxora API",
    description="AI-powered bookkeeping and tax-preparation platform for Pakistani businesses",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend", "index.html")

@app.get("/")
def root():
    return FileResponse(FRONTEND_PATH)

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

@app.post("/extract-and-export")
async def extract_and_export(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"error": "Only JPG and PNG files are supported"}
        )
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extracted = extract_invoice_data(file_path, file.content_type)
    base_name = os.path.splitext(file.filename)[0]
    excel_path = export_to_excel(extracted, base_name)
    return FileResponse(
        path=excel_path,
        filename=f"{base_name}_taxora.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.post("/extract-and-tax")
async def extract_and_tax(file: UploadFile = File(...), is_filer: bool = True):
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"error": "Only JPG and PNG files are supported"}
        )
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extracted = extract_invoice_data(file_path, file.content_type)
    tax_result = process_invoice_tax(extracted, is_filer)
    return {
        "message": "Extraction and tax calculation complete",
        "filename": file.filename,
        "extracted_data": extracted,
        "tax_calculation": tax_result
    }