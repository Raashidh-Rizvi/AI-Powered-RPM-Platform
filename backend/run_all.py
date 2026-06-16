import subprocess
import sys
import time

def main():
    services = [
        {"name": "patient_service", "port": 8001},
        {"name": "rpm_service", "port": 8002},
        {"name": "ai_service", "port": 8003},
        {"name": "api_gateway", "port": 8000},
    ]

    processes = []

    print("Starting all AI-Powered RPM microservices...\n")

    try:
        for svc in services:
            print(f"[*] Starting {svc['name']} on port {svc['port']}...")
            # Using uvicorn via python -m ensures the correct virtualenv python is used
            proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", f"{svc['name']}.main:app", "--host", "0.0.0.0", "--port", str(svc['port'])],
            )
            processes.append(proc)
            time.sleep(1) # Give each service a second to bind its port

        print("\nAll services are running! Press Ctrl+C to stop them all.\n")
        
        # Wait for processes to exit
        for proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for proc in processes:
            proc.terminate()
            proc.wait()
        print("All services stopped.")

if __name__ == "__main__":
    main()
