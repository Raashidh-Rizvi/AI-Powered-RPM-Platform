import random
import uuid
from datetime import datetime, timedelta
from shared.database import SessionLocal, engine, Base
from shared import models
from shared import schemas
from shared import crud

def seed():
    print("Dropping old tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Seeding database...")
    
    # Create 3 patients
    patients_data = ["John Doe", "Jane Smith", "Robert Williams"]
    patients = []
    
    for name in patients_data:
        p = crud.create_patient(db, schemas.PatientCreate(name=name))
        patients.append(p)

    # 7 Vitals
    vitals = ["BP_SYS", "BP_DIA", "HR", "SpO2", "TEMP", "RESP_RATE", "GLUCOSE"]

    for i, p in enumerate(patients):
        print(f"Seeding 1000 readings for each of the 7 vitals for patient {i+1}/3: {p.name}")
        readings = []
        for vital in vitals:
            for j in range(1000):
                if vital == "BP_SYS":
                    val = random.randint(100, 180)
                elif vital == "BP_DIA":
                    val = random.randint(60, 110)
                elif vital == "HR":
                    val = random.randint(50, 120)
                elif vital == "SpO2":
                    val = random.randint(85, 100)
                elif vital == "TEMP":
                    val = round(random.uniform(97.0, 102.0), 1)
                elif vital == "RESP_RATE":
                    val = random.randint(12, 25)
                elif vital == "GLUCOSE":
                    val = random.randint(70, 140)
                
                reading = models.RPMReading(
                    id=str(uuid.uuid4()),
                    patient_id=p.id,
                    vital_type=vital,
                    value=val,
                    timestamp=datetime.utcnow() - timedelta(hours=j)
                )
                readings.append(reading)
        
        # Insert readings for this patient
        db.bulk_save_objects(readings)
        db.commit()

    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed()
