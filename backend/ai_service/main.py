from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from shared.database import engine, Base, get_db
from shared import schemas
from shared import crud

# Import worker logic
from ai_service.worker import process_rpm_reading

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Service", description="RPM Platform AI Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-service"}

class AIProcessRequest(BaseModel):
    reading_id: str

@app.post("/ai/process/{patient_id}")
async def process_rpm_data(patient_id: str, request: AIProcessRequest, background_tasks: BackgroundTasks):
    # This endpoint is called by rpm-service to trigger AI processing
    background_tasks.add_task(process_rpm_reading, request.reading_id, patient_id)
    return {"status": "processing initiated", "patient_id": patient_id, "reading_id": request.reading_id}

@app.get("/alerts/", response_model=List[schemas.AIAlert])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_alerts(db, skip=skip, limit=limit)

@app.get("/ai/risk/{patient_id}", response_model=List[schemas.AIRiskScore])
def read_patient_risk(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_risk_scores(db, patient_id=patient_id, skip=skip, limit=limit)

@app.get("/ai/anomalies/{patient_id}", response_model=List[schemas.AIAnomaly])
def read_patient_anomalies(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_anomalies(db, patient_id=patient_id, skip=skip, limit=limit)

@app.get("/ai/trends/{patient_id}", response_model=List[schemas.AITrend])
def read_patient_trends(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_trends(db, patient_id=patient_id, skip=skip, limit=limit)

@app.get("/ai/features/{patient_id}", response_model=List[schemas.AIFeature])
def read_patient_features(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_ai_features(db, patient_id=patient_id, skip=skip, limit=limit)
