# Local Execution Guide

This guide provides instructions on how to run the AI-Powered RPM Platform locally. The backend has been refactored into a microservices architecture.

## Prerequisites
- **Docker & Docker Compose** (Recommended for backend)
- **Python 3.10+** installed (If running without Docker)
- **Node.js 18+** installed (For the frontend)
- **PostgreSQL & Redis**: If running without Docker, you need local instances running on `5432` and `6379`.

---

## 1. Running the Backend Microservices

### Option A: Using Docker Compose (Recommended)

This is the easiest way to run the database, redis, and all the Python microservices simultaneously.

1. Open a terminal and navigate to the docker directory:
   ```bash
   cd backend/docker
   ```

2. Start the services:
   ```bash
   docker-compose up --build
   ```

*(This will bring up the API Gateway on `http://localhost:8000`, along with all underlying services).*

### Option B: Running Locally without Docker (Single Terminal)

If you prefer to run the services bare-metal without Docker, you can run all services simultaneously using the unified startup script:

1. **Install Dependencies** (Run once in the backend directory):
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run all microservices at once**:
   ```bash
   cd backend
   python run_all.py
   ```

*(This will automatically start the Patient Service, RPM Service, AI Service, and API Gateway on their respective ports. The Gateway will be available at `http://localhost:8000`)*

*(Optional)* To seed the database, run:
```bash
cd backend
python seed.py
```

---

## 2. Running the Frontend (Angular)

Open a **separate terminal window** and navigate to the frontend directory:

```bash
cd frontend
```

Install the Node.js dependencies:

```bash
npm install
```

Start the Angular development server:

```bash
npm start
```
*(Alternatively, use `ng serve` if you have the Angular CLI installed globally).*

The frontend application will compile and be available at `http://localhost:4200`. It is configured to automatically communicate with your API Gateway running on port 8000.
