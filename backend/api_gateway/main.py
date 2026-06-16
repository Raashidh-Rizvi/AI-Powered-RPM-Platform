import os
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API Gateway", description="Central Entry Point for RPM Microservices")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://localhost:8001")
RPM_SERVICE_URL = os.getenv("RPM_SERVICE_URL", "http://localhost:8002")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8003")

# We will use httpx to proxy the requests

async def proxy_request(url: str, request: Request):
    async with httpx.AsyncClient() as client:
        # Read the body if it's a POST/PUT/PATCH
        body = await request.body()
        headers = dict(request.headers)
        # Remove the host header so the proxy works correctly
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body
            )
            return Response(content=response.content, status_code=response.status_code, headers=dict(response.headers))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "api-gateway"}

# Patient Service Routes
@app.api_route("/patients/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_patients(path: str, request: Request):
    url = f"{PATIENT_SERVICE_URL}/patients/{path}"
    if not path:
        url = f"{PATIENT_SERVICE_URL}/patients/"
    return await proxy_request(url, request)

# RPM Service Routes
@app.api_route("/rpm/readings/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_rpm(path: str, request: Request):
    url = f"{RPM_SERVICE_URL}/rpm/readings/{path}"
    if not path:
        url = f"{RPM_SERVICE_URL}/rpm/readings"
    return await proxy_request(url, request)

@app.api_route("/rpm/readings", methods=["POST", "GET"])
async def proxy_rpm_root(request: Request):
    url = f"{RPM_SERVICE_URL}/rpm/readings"
    return await proxy_request(url, request)

@app.api_route("/vitals/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_vitals(path: str, request: Request):
    url = f"{RPM_SERVICE_URL}/vitals/{path}"
    if not path:
        url = f"{RPM_SERVICE_URL}/vitals"
    return await proxy_request(url, request)

@app.api_route("/vitals", methods=["POST", "GET"])
async def proxy_vitals_root(request: Request):
    url = f"{RPM_SERVICE_URL}/vitals"
    return await proxy_request(url, request)

# AI Service Routes
@app.api_route("/alerts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_alerts(path: str, request: Request):
    url = f"{AI_SERVICE_URL}/alerts/{path}"
    if not path:
        url = f"{AI_SERVICE_URL}/alerts/"
    return await proxy_request(url, request)

# AI Service AI Routes
@app.api_route("/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ai(path: str, request: Request):
    url = f"{AI_SERVICE_URL}/ai/{path}"
    if not path:
        url = f"{AI_SERVICE_URL}/ai/"
    return await proxy_request(url, request)
