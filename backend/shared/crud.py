from sqlalchemy.orm import Session
from sqlalchemy import func
from shared import models
from shared import schemas
from datetime import datetime, timedelta

def get_patient(db: Session, patient_id: str):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(name=patient.name)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def create_rpm_reading(db: Session, reading: schemas.RPMReadingCreate):
    db_reading = models.RPMReading(**reading.model_dump(exclude_unset=True))
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_recent_reading(db: Session, patient_id: str, vital_type: str, minutes: int = 5):
    time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
    return db.query(models.RPMReading).filter(
        models.RPMReading.patient_id == patient_id,
        models.RPMReading.vital_type == vital_type,
        models.RPMReading.timestamp >= time_threshold
    ).first()

def get_rpm_readings(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.RPMReading).filter(models.RPMReading.patient_id == patient_id).order_by(models.RPMReading.timestamp.desc()).offset(skip).limit(limit).all()

def get_vitals_by_range(db: Session, patient_id: str, days: int = 7):
    time_threshold = datetime.utcnow() - timedelta(days=days)
    return db.query(models.RPMReading).filter(
        models.RPMReading.patient_id == patient_id,
        models.RPMReading.timestamp >= time_threshold
    ).order_by(models.RPMReading.timestamp.asc()).all()

def get_latest_vitals(db: Session, patient_id: str):
    subquery = db.query(
        models.RPMReading.vital_type,
        func.max(models.RPMReading.timestamp).label('max_timestamp')
    ).filter(models.RPMReading.patient_id == patient_id).group_by(models.RPMReading.vital_type).subquery()
    
    return db.query(models.RPMReading).join(
        subquery,
        (models.RPMReading.vital_type == subquery.c.vital_type) &
        (models.RPMReading.timestamp == subquery.c.max_timestamp)
    ).filter(models.RPMReading.patient_id == patient_id).all()

def get_alerts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AIAlert).order_by(models.AIAlert.created_at.desc()).offset(skip).limit(limit).all()

def get_risk_scores(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AIRiskScore).filter(models.AIRiskScore.patient_id == patient_id).order_by(models.AIRiskScore.calculated_at.desc()).offset(skip).limit(limit).all()

def get_anomalies(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AIAnomaly).filter(models.AIAnomaly.patient_id == patient_id).order_by(models.AIAnomaly.created_at.desc()).offset(skip).limit(limit).all()

def get_trends(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AITrend).filter(models.AITrend.patient_id == patient_id).order_by(models.AITrend.created_at.desc()).offset(skip).limit(limit).all()

def get_ai_features(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AIFeature).filter(models.AIFeature.patient_id == patient_id).order_by(models.AIFeature.created_at.desc()).offset(skip).limit(limit).all()
