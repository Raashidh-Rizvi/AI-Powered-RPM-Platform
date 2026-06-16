from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from typing import List
import models
import schemas
import crud
from worker import process_rpm_reading

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered RPM Platform", description="RPM Platform API with AI processing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-Powered RPM Platform API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "services": {"db": "ok", "redis": "ok", "ai_engine": "ok"}}

@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db=db, patient=patient)

@app.get("/patients/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_patients(db, skip=skip, limit=limit)

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: str, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.post("/rpm/readings", response_model=schemas.RPMReading)
def create_rpm_reading(
    reading: schemas.RPMReadingCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    # Ensure patient exists, or optionally create
    db_patient = crud.get_patient(db, patient_id=reading.patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db_reading = crud.create_rpm_reading(db=db, reading=reading)
    
    # Trigger AI Processing Engine (using FastAPI background tasks instead of Celery for local testing without Redis)
    background_tasks.add_task(process_rpm_reading, str(db_reading.id), str(reading.patient_id))
    
    return db_reading

@app.get("/patients/{patient_id}/readings/", response_model=List[schemas.RPMReading])
def read_readings_for_patient(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_rpm_readings(db, patient_id=patient_id, skip=skip, limit=limit)

@app.get("/alerts/", response_model=List[schemas.AIAlert])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_alerts(db, skip=skip, limit=limit)

@app.get("/patients/{patient_id}/risk", response_model=List[schemas.AIRiskScore])
def read_patient_risk(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_risk_scores(db, patient_id=patient_id, skip=skip, limit=limit)

@app.get("/patients/{patient_id}/anomalies", response_model=List[schemas.AIAnomaly])
def read_patient_anomalies(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_anomalies(db, patient_id=patient_id, skip=skip, limit=limit)

@app.get("/patients/{patient_id}/trends", response_model=List[schemas.AITrend])
def read_patient_trends(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_trends(db, patient_id=patient_id, skip=skip, limit=limit)
