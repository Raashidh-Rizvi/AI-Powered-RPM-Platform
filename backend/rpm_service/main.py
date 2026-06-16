import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import logging
from datetime import datetime

from shared.database import engine, Base, get_db
from shared import schemas
from shared import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RPM Service", description="RPM Platform Data Ingestion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8003")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rpm-service"}

@app.post("/vitals/record", response_model=schemas.RPMReading)
async def create_rpm_reading(
    reading: schemas.RPMReadingCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    # Validation 1: Patient exists
    db_patient = crud.get_patient(db, patient_id=reading.patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Validation 2: Reject future timestamps
    if reading.timestamp and reading.timestamp > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid timestamp: cannot be in the future")
    
    # Validation 3: Ranges
    if reading.vital_type.upper() == "SPO2":
        if reading.value is not None and (reading.value < 0 or reading.value > 100):
            raise HTTPException(status_code=400, detail="Invalid SpO2 value: must be between 0 and 100")
            
    # Validation 4: Duplicate entries within short window (e.g., 1 minute)
    recent = crud.get_recent_reading(db, reading.patient_id, reading.vital_type, minutes=1)
    if recent:
        raise HTTPException(status_code=409, detail="Duplicate vital reading detected within 1 minute")
    
    db_reading = crud.create_rpm_reading(db=db, reading=reading)
    
    # Asynchronously call the AI service to process the reading
    async def trigger_ai(reading_id: str, patient_id: str):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{AI_SERVICE_URL}/ai/process/{patient_id}",
                    json={"reading_id": reading_id}
                )
        except Exception as e:
            logger.error(f"Failed to trigger AI service: {e}")

    background_tasks.add_task(trigger_ai, str(db_reading.id), str(reading.patient_id))
    
    return db_reading

def format_visualization_response(patient_id: str, readings) -> List[schemas.VitalTimeSeriesResponse]:
    grouped_data = {}
    for r in readings:
        if r.vital_type not in grouped_data:
            grouped_data[r.vital_type] = []
        grouped_data[r.vital_type].append(schemas.DataPoint(time=r.timestamp, value=r.value, structured_value=r.structured_value))
    
    return [
        schemas.VitalTimeSeriesResponse(patient_id=patient_id, vital_type=vt, data_points=dp)
        for vt, dp in grouped_data.items()
    ]

@app.get("/vitals/{patient_id}", response_model=List[schemas.VitalTimeSeriesResponse])
def read_vitals_for_patient(patient_id: str, range: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if range == "7d":
        readings = crud.get_vitals_by_range(db, patient_id, days=7)
    elif range == "30d":
        readings = crud.get_vitals_by_range(db, patient_id, days=30)
    else:
        readings = crud.get_rpm_readings(db, patient_id=patient_id, skip=0, limit=1000)
    return format_visualization_response(patient_id, readings)

@app.get("/vitals/latest/{patient_id}", response_model=List[schemas.VitalTimeSeriesResponse])
def read_latest_vitals(patient_id: str, db: Session = Depends(get_db)):
    readings = crud.get_latest_vitals(db, patient_id=patient_id)
    return format_visualization_response(patient_id, readings)

@app.get("/rpm/readings/{patient_id}", response_model=List[schemas.RPMReading])
def read_readings_for_patient_legacy(patient_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_rpm_readings(db, patient_id=patient_id, skip=skip, limit=limit)
