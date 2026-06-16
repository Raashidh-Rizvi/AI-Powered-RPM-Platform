import requests
import json
import time

base_url = "http://localhost:8002"

patient_id = "123" # seeded by recreate_db.py

def test_vitals():
    print("Testing SpO2 validation (should pass)...")
    resp = requests.post(f"{base_url}/vitals/record", json={
        "patient_id": patient_id,
        "vital_type": "SPO2",
        "value": 92.0,
        "unit": "%",
        "device_source": "PulseOximeter"
    })
    print(resp.status_code, resp.json())
    
    print("\nTesting SpO2 invalid range (should fail)...")
    resp = requests.post(f"{base_url}/vitals/record", json={
        "patient_id": patient_id,
        "vital_type": "SPO2",
        "value": 105.0
    })
    print(resp.status_code, resp.json())
    
    print("\nTesting duplicate within 1 min (should fail)...")
    resp = requests.post(f"{base_url}/vitals/record", json={
        "patient_id": patient_id,
        "vital_type": "SPO2",
        "value": 90.0
    })
    print(resp.status_code, resp.json())
    
    print("\nTesting BP structured value...")
    resp = requests.post(f"{base_url}/vitals/record", json={
        "patient_id": patient_id,
        "vital_type": "BP_SYS",
        "value": 125.0,
        "structured_value": {"systolic": 125, "diastolic": 80},
        "unit": "mmHg"
    })
    print(resp.status_code, resp.json())
    
    # Wait for celery/background tasks to run
    print("\nWaiting for AI processing...")
    time.sleep(2)
    
    print("\nFetching features...")
    resp = requests.get(f"http://localhost:8003/ai/features/{patient_id}")
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    test_vitals()
