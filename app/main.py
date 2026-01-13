from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.schemas import PredictRequest, PredictResponse
from app.model import predict_intent, load_model
from app.utils import extract_attributes
from app.deps import get_db
from app.models import Product, SearchQuery

app = FastAPI(title="AI Search Backend")


@app.on_event("startup")
def startup_event():
    load_model()
    print("✅ ML model loaded")



@app.get("/health")
def health():
    return {"status": "ok"}



@app.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")



@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, db: Session = Depends(get_db)):
    intent, confidence = predict_intent(req.text)

    
    search_record = SearchQuery(
        query_text=req.text,
        intent=intent,
        confidence=str(confidence)
    )
    db.add(search_record)
    db.commit()
    db.refresh(search_record)

    return PredictResponse(intent=intent, confidence=confidence)



@app.post("/search")
def search(req: PredictRequest, db: Session = Depends(get_db)):

    
    intent, confidence = predict_intent(req.text)

   
    attributes = extract_attributes(req.text, intent)

    
    query = db.query(Product)
    for key, value in attributes.items():
        if value is not None:  # include 0/False
            query = query.filter(getattr(Product, key) == value)
    products = query.all()

    
    search_record = SearchQuery(
        query_text=req.text,
        intent=intent,
        confidence=str(confidence)
    )
    db.add(search_record)
    db.commit()
    db.refresh(search_record) 

   
    return {
        "intent": intent,
        "confidence": confidence,
        "attributes": attributes,
        "results": [
            {"id": p.id, "name": p.name} for p in products
        ],
        "search_id": search_record.id
    }
