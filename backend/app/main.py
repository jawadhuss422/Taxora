from fastapi import FastAPI

app = FastAPI(
    title="Taxora API",
    description="AI-powered bookkeeping and tax-preparation platform for Pakistani businesses",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "Taxora API is running", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}