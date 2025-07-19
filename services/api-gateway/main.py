from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from datetime import datetime
import json

app = FastAPI(title="CodeVoice API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "speech": "http://speech-service:8001",
    "code": "http://code-service:8002", 
    "code-review": "http://code-review-service:8003",
    "collaboration": "http://collaboration-service:8004",
    "weather": "http://weather-service:8007",
    "live-ai-coding": "http://live-ai-coding-service:8005",
    "collaborative-docs": "http://collaborative-docs-service:8006"
}

# Rate limiting (simple in-memory)
request_counts = {}
RATE_LIMIT = 100  # requests per minute

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = datetime.now()
    
    # Clean old entries
    if client_ip in request_counts:
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if (current_time - req_time).seconds < 60
        ]
    else:
        request_counts[client_ip] = []
    
    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    """Health check for all services"""
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
    
    return {
        "gateway": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": health_status
    }

# Speech Service Routes
@app.post("/api/transcribe")
async def transcribe_audio(request: Request):
    """Forward audio transcription request to speech service"""
    async with httpx.AsyncClient() as client:
        try:
            body = await request.json()
            response = await client.post(f"{SERVICES['speech']}/api/transcribe", json=body)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Speech service error: {str(e)}")

# Code Service Routes
@app.post("/api/code/generate")
async def generate_code(request: Request):
    """Forward code generation request to code service"""
    async with httpx.AsyncClient() as client:
        try:
            body = await request.json()
            response = await client.post(f"{SERVICES['code']}/api/code/generate", json=body)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Code service error: {str(e)}")

# Code Review Service Routes
@app.post("/api/code/review")
async def review_code(request: Request):
    """Forward code review request to code review service"""
    async with httpx.AsyncClient() as client:
        try:
            body = await request.json()
            response = await client.post(f"{SERVICES['code-review']}/api/code/review", json=body)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Code review service error: {str(e)}")

# Collaboration Service Routes
@app.post("/api/collaboration/join")
async def join_session(request: Request):
    """Forward collaboration join request"""
    async with httpx.AsyncClient() as client:
        try:
            body = await request.json()
            response = await client.post(f"{SERVICES['collaboration']}/api/collaboration/join", json=body)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaboration service error: {str(e)}")

# Weather Service Routes
@app.get("/api/weather/{city}")
async def get_weather(city: str):
    """Forward weather request to weather service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['weather']}/api/weather/{city}")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Weather service error: {str(e)}")

# Live AI Coding Service Routes
@app.post("/api/live-coding/generate")
async def generate_live_code(request: Request):
    """Forward live AI coding request"""
    async with httpx.AsyncClient() as client:
        try:
            body = await request.json()
            response = await client.post(f"{SERVICES['live-ai-coding']}/api/live-coding/generate", json=body)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Live AI coding service error: {str(e)}")

@app.post("/api/live-coding/session/create")
async def create_live_session(session_name: str, user_id: str):
    """Create a new live coding session"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['live-ai-coding']}/api/live-coding/session/create",
                params={"session_name": session_name, "user_id": user_id}
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Live AI coding service error: {str(e)}")

@app.get("/api/live-coding/session/{session_id}")
async def get_live_session(session_id: str):
    """Get live coding session details"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['live-ai-coding']}/api/live-coding/session/{session_id}")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Live AI coding service error: {str(e)}")

@app.get("/api/live-coding/sessions")
async def list_live_sessions():
    """List all live coding sessions"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['live-ai-coding']}/api/live-coding/sessions")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Live AI coding service error: {str(e)}")

# Collaborative Documents Service Routes
@app.post("/api/documents/create")
async def create_document(title: str, language: str, user_id: str, username: str):
    """Create a new collaborative document"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['collaborative-docs']}/api/documents/create",
                params={"title": title, "language": language, "user_id": user_id, "username": username}
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaborative docs service error: {str(e)}")

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get document details"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['collaborative-docs']}/api/documents/{doc_id}")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaborative docs service error: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """List all documents"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['collaborative-docs']}/api/documents")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaborative docs service error: {str(e)}")

@app.post("/api/documents/{doc_id}/update")
async def update_document(doc_id: str, request: Request):
    """Update document content"""
    async with httpx.AsyncClient() as client:
        try:
            body = await request.json()
            response = await client.post(
                f"{SERVICES['collaborative-docs']}/api/documents/{doc_id}/update",
                json=body
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaborative docs service error: {str(e)}")

@app.post("/api/documents/{doc_id}/comment")
async def add_document_comment(doc_id: str, request: Request):
    """Add a comment to a document"""
    async with httpx.AsyncClient() as client:
        try:
            body = await request.json()
            response = await client.post(
                f"{SERVICES['collaborative-docs']}/api/documents/{doc_id}/comment",
                json=body
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaborative docs service error: {str(e)}")

@app.get("/api/documents/{doc_id}/comments")
async def get_document_comments(doc_id: str):
    """Get all comments for a document"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['collaborative-docs']}/api/documents/{doc_id}/comments")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaborative docs service error: {str(e)}")

@app.get("/api/documents/{doc_id}/versions")
async def get_document_versions(doc_id: str):
    """Get version history of a document"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICES['collaborative-docs']}/api/documents/{doc_id}/versions")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Collaborative docs service error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 