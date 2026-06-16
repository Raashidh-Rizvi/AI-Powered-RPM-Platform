# Local Execution Guide

This guide provides instructions on how to run the AI-Powered RPM Platform locally, running the frontend and backend services separately (without Docker).

## Prerequisites
- **Python 3.10+** installed
- **Node.js 18+** installed
- **PostgreSQL**: A local instance running on port `5432` with a database named `AI-Powered RPM Platform` owned by the user `postgres` with password `rdh123`.

## 1. Running the Backend (FastAPI)

Open a new terminal and navigate to the backend directory:

```bash
cd backend
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

*(Optional)* If you haven't already, seed the database with initial patients and alerts:

```bash
python seed.py
```

Start the FastAPI development server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.

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

The frontend application will compile and be available at `http://localhost:4200`. It is configured to automatically communicate with your local backend API running on port 8000.
