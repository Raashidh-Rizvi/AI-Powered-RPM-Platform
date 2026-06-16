import os
import sys
from shared.database import engine, SessionLocal, Base
from shared import models

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Seeding test patient 123...")
db = SessionLocal()
try:
    test_patient = models.Patient(id="123", name="Test Patient")
    db.add(test_patient)
    db.commit()
    print("Database seeded successfully.")
except Exception as e:
    print(f"Error seeding: {e}")
finally:
    db.close()
