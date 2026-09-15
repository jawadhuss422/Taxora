from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
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

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Taxora - AI Invoice Extraction</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; color: #1a1a2e; }
    header { background: #1F4E79; color: white; padding: 20px 40px; display: flex; align-items: center; gap: 15px; }
    header h1 { font-size: 28px; letter-spacing: 1px; }
    header p { font-size: 13px; opacity: 0.8; }
    .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
    .upload-card { background: white; border-radius: 16px; padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
    .upload-card h2 { font-size: 22px; color: #1F4E79; margin-bottom: 8px; }
    .upload-card p { color: #666; margin-bottom: 30px; font-size: 14px; }
    .drop-zone { border: 2px dashed #1F4E79; border-radius: 12px; padding: 50px 20px; cursor: pointer; transition: background 0.2s; margin-bottom: 20px; }
    .drop-zone:hover { background: #f0f7ff; }
    .drop-zone input { display: none; }
    .drop-zone .icon { font-size: 48px; margin-bottom: 10px; }
    .drop-zone p { color: #1F4E79; font-weight: 600; margin-bottom: 5px; }
    .drop-zone span { font-size: 12px; color: #999; }
    #file-name { font-size: 13px; color: #444; margin-bottom: 20px; min-height: 20px; }
    .btn { background: #1F4E79; color: white; border: none; padding: 14px 40px; border-radius: 8px; font-size: 16px; cursor: pointer; transition: background 0.2s; width: 100%; max-width: 300px; }
    .btn:hover { background: #163d61; }
    .btn:disabled { background: #aaa; cursor: not-allowed; }
    .loader { display: none; margin: 20px auto; width: 40px; height: 40px; border: 4px solid #ddd; border-top: 4px solid #1F4E79; border-radius: 50%; animation: spin 0.8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .results-card { display: none; background: white; border-radius: 16px; padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-top: 30px; }
    .results-card h2 { color: #1F4E79; margin-bottom: 20px; font-size: 20px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
    th { background: #1F4E79; color: white; padding: 12px 16px; text-align: left; font-size: 14px; }
    td { padding: 12px 16px; border-bottom: 1px solid #eee; font-size: 14px; }
    tr:hover td { background: #f9f9f9; }
    .field-label { font-weight: 600; color: #333; width: 200px; }
    .download-btn { background: #27ae60; color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 15px; cursor: pointer; transition: background 0.2s; }
    .download-btn:hover { background: #219a52; }
    .error-msg { display: none; background: #fee; border: 1px solid #fcc; color: #c00; padding: 15px; border-radius: 8px; margin-top: 15px; font-size: 14px; }
    .success-badge { display: inline-block; background: #e8f5e9; color: #27ae60; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-left: 10px; }
  </style>
</head>
<body>
<header>
  <div>
    <h1>⚡ Taxora</h1>
    <p>AI-powered Invoice & Tax Data Extraction for Pakistani Businesses</p>
  </div>
</header>
<div class="container">
  <div class="upload-card">
    <h2>Upload Your Invoice</h2>
    <p>Supports JPG and PNG invoice images. AI will extract all fields automatically.</p>
    <div class="drop-zone" onclick="document.getElementById('fileInput').click()">
      <input type="file" id="fileInput" accept=".jpg,.jpeg,.png" onchange="handleFile(this)"/>
      <div class="icon">📄</div>
      <p>Click to upload invoice</p>
      <span>JPG, PNG supported</span>
    </div>
    <div id="file-name">No file selected</div>
    <button class="btn" id="extractBtn" onclick="extractInvoice()" disabled>
      🔍 Extract with AI
    </button>
    <div class="loader" id="loader"></div>
    <div class="error-msg" id="errorMsg"></div>
  </div>
  <div class="results-card" id="resultsCard">
    <h2>Extracted Data <span class="success-badge">✓ Complete</span></h2>
    <table id="resultsTable">
      <thead><tr><th>Field</th><th>Extracted Value</th></tr></thead>
      <tbody id="resultsBody"></tbody>
    </table>
    <button class="download-btn" id="downloadBtn" onclick="downloadExcel()">
      📥 Download Excel Report
    </button>
  </div>
</div>
<script>
  let selectedFile = null;
  function handleFile(input) {
    selectedFile = input.files[0];
    if (selectedFile) {
      document.getElementById('file-name').textContent = '📎 ' + selectedFile.name;
      document.getElementById('extractBtn').disabled = false;
    }
  }
  async function extractInvoice() {
    if (!selectedFile) return;
    document.getElementById('loader').style.display = 'block';
    document.getElementById('extractBtn').disabled = true;
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('errorMsg').style.display = 'none';
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await fetch('/extract', { method: 'POST', body: formData });
      const data = await response.json();
      document.getElementById('loader').style.display = 'none';
      document.getElementById('extractBtn').disabled = false;
      if (data.extracted_data) { displayResults(data.extracted_data); }
      else { showError('Extraction failed. Please try another image.'); }
    } catch (err) {
      document.getElementById('loader').style.display = 'none';
      document.getElementById('extractBtn').disabled = false;
      showError('Could not connect to server.');
    }
  }
  function displayResults(data) {
    const labels = {
      supplier_name: 'Supplier Name', invoice_number: 'Invoice Number',
      invoice_date: 'Invoice Date', due_date: 'Due Date',
      description: 'Description', subtotal: 'Subtotal',
      sales_tax: 'Sales Tax', withholding_tax: 'Withholding Tax',
      total_amount: 'Total Amount', currency: 'Currency', payment_method: 'Payment Method'
    };
    const tbody = document.getElementById('resultsBody');
    tbody.innerHTML = '';
    for (const [key, label] of Object.entries(labels)) {
      tbody.innerHTML += `<tr><td class="field-label">${label}</td><td>${data[key] || '-'}</td></tr>`;
    }
    document.getElementById('resultsCard').style.display = 'block';
  }
  async function downloadExcel() {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('file', selectedFile);
    const response = await fetch('/extract-and-export', { method: 'POST', body: formData });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = selectedFile.name.replace(/\\.[^/.]+$/, '') + '_taxora.xlsx';
    a.click();
  }
  function showError(msg) {
    const el = document.getElementById('errorMsg');
    el.textContent = msg;
    el.style.display = 'block';
  }
</script>
</body>
</html>
"""

@app.get("/")
def root():
    return HTMLResponse(content=HTML)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(status_code=400, content={"error": "Only PDF, JPG and PNG files are allowed"})
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "File uploaded successfully", "filename": file.filename, "content_type": file.content_type, "status": "uploaded"}

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(status_code=400, content={"error": "Only JPG and PNG files are supported"})
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extracted = extract_invoice_data(file_path, file.content_type)
    return {"message": "Extraction complete", "filename": file.filename, "extracted_data": extracted}

@app.post("/extract-and-export")
async def extract_and_export(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(status_code=400, content={"error": "Only JPG and PNG files are supported"})
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extracted = extract_invoice_data(file_path, file.content_type)
    base_name = os.path.splitext(file.filename)[0]
    excel_path = export_to_excel(extracted, base_name)
    return FileResponse(path=excel_path, filename=f"{base_name}_taxora.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.post("/extract-and-tax")
async def extract_and_tax(file: UploadFile = File(...), is_filer: bool = True):
    allowed_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        return JSONResponse(status_code=400, content={"error": "Only JPG and PNG files are supported"})
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extracted = extract_invoice_data(file_path, file.content_type)
    tax_result = process_invoice_tax(extracted, is_filer)
    return {"message": "Extraction and tax calculation complete", "filename": file.filename, "extracted_data": extracted, "tax_calculation": tax_result}