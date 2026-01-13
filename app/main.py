from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.schemas import PredictRequest, PredictResponse
from app.model import predict_intent, load_model
from app.utils import extract_attributes
from app.deps import get_db
from app.models import Product

app = FastAPI(title="AI Search Backend")

# -----------------------------
# Load ML model on startup
# -----------------------------
@app.on_event("startup")
def startup_event():
    load_model()
    print("✅ ML model loaded")

# -----------------------------
# Health Check Endpoint
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Database Health Check
# -----------------------------
@app.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}

# -----------------------------
# Predict Intent Endpoint
# -----------------------------
@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    intent, confidence = predict_intent(req.text)
    return PredictResponse(intent=intent, confidence=confidence)

# -----------------------------
# Search Endpoint (PostgreSQL)
# -----------------------------
@app.post("/search")
def search(req: PredictRequest, db: Session = Depends(get_db)):

    # 1️⃣ ML predicts intent
    intent, confidence = predict_intent(req.text)

    # 2️⃣ Extract attributes
    attributes = extract_attributes(req.text, intent)

    # 3️⃣ Build dynamic query
    query = db.query(Product)
    for key, value in attributes.items():
        if value:
            query = query.filter(getattr(Product, key) == value)

    products = query.all()

    # 4️⃣ Return results
    return {
        "intent": intent,
        "confidence": confidence,
        "attributes": attributes,
        "results": [
            {"id": p.id, "name": p.name} for p in products
        ]
    }
