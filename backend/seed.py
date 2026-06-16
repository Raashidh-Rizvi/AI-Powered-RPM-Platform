import uuid
from datetime import datetime, timedelta
import random
from database import SessionLocal, engine, Base
import models
import schemas
import crud

def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if we already have patients
    if db.query(models.Patient).count() > 0:
        print("Database already seeded.")
        return

    print("Seeding database...")
    
    # Create a specific patient for the Postman test
    test_patient = models.Patient(id="123", name="Test Patient")
    db.add(test_patient)
    db.commit()
    db.refresh(test_patient)

    # Create other patients
    patients_data = ["John Doe", "Jane Smith", "Robert Williams", "Emily Chen", "Michael Johnson"]
    patients = [test_patient]
    
    for name in patients_data:
        p = crud.create_patient(db, schemas.PatientCreate(name=name))
        patients.append(p)

    # Create some mock alerts
    alerts_data = [
        {
            "patient_id": patients[0].id,
            "alert_type": "Deterioration",
            "severity": "CRITICAL",
            "priority_score": 92,
            "message": "Sustained BP increase (165/105). 92% confidence of deterioration.",
            "explanation": "Patient has exhibited a 15% increase in baseline blood pressure over 3 days.",
            "source_engine": "Early Deterioration Engine",
            "status": "open"
        },
        {
            "patient_id": patients[1].id,
            "alert_type": "Anomaly",
            "severity": "HIGH",
            "priority_score": 75,
            "message": "SpO2 dropped below 88% twice in the last hour.",
            "explanation": "Sudden drop in oxygen saturation detected outside normal bounds.",
            "source_engine": "Anomaly Detection Engine",
            "status": "open"
        }
    ]

    for a_data in alerts_data:
        db_alert = models.AIAlert(**a_data)
        db.add(db_alert)

    # Add 1000 readings for the first 3 patients
    for i in range(3):
        if i < len(patients):
            for j in range(1000):
                m_type = random.choice(["BP_SYS", "BP_DIA", "HR", "SpO2", "TEMP"])
                if m_type == "BP_SYS":
                    val = random.randint(100, 180)
                elif m_type == "BP_DIA":
                    val = random.randint(60, 110)
                elif m_type == "HR":
                    val = random.randint(50, 120)
                elif m_type == "SpO2":
                    val = random.randint(85, 100)
                else:
                    val = round(random.uniform(97.0, 102.0), 1)
                
                reading = models.RPMReading(
                    patient_id=patients[i].id,
                    metric_type=m_type,
                    value=val,
                    timestamp=datetime.utcnow() - timedelta(hours=j)
                )
                db.add(reading)
        
    db.commit()
    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed()
