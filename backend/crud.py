from sqlalchemy.orm import Session
import models
import schemas

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
    db_reading = models.RPMReading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_rpm_readings(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.RPMReading).filter(models.RPMReading.patient_id == patient_id).offset(skip).limit(limit).all()

def get_alerts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AIAlert).order_by(models.AIAlert.created_at.desc()).offset(skip).limit(limit).all()

def get_risk_scores(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AIRiskScore).filter(models.AIRiskScore.patient_id == patient_id).order_by(models.AIRiskScore.calculated_at.desc()).offset(skip).limit(limit).all()

def get_anomalies(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AIAnomaly).filter(models.AIAnomaly.patient_id == patient_id).order_by(models.AIAnomaly.created_at.desc()).offset(skip).limit(limit).all()

def get_trends(db: Session, patient_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AITrend).filter(models.AITrend.patient_id == patient_id).order_by(models.AITrend.created_at.desc()).offset(skip).limit(limit).all()
