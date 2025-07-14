from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import redis
import json
import time
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import Counter, Histogram
import os
from typing import Optional
from pydantic import BaseModel

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

app = FastAPI(
    title="CodeVoice API Gateway",
    description="Microservices API Gateway for CodeVoice Platform",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://codevoice.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

# Redis connection
redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

# Service URLs (in production, use service discovery)
SERVICES = {
    "speech": os.getenv("SPEECH_SERVICE_URL", "http://speech-service:8001"),
    "code": os.getenv("CODE_SERVICE_URL", "http://code-service:8002"),
    "weather": os.getenv("WEATHER_SERVICE_URL", "http://weather-service:8003"),
    "task": os.getenv("TASK_SERVICE_URL", "http://task-service:8004"),
    "user": os.getenv("USER_SERVICE_URL", "http://user-service:8005"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8006"),
    "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8007"),
}

class ServiceHealth:
    def __init__(self):
        self.health_status = {}
    
    async def check_service_health(self, service_name: str, service_url: str):
        """Check if a service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                self.health_status[service_name] = response.status_code == 200
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {service_name}", error=str(e))
            self.health_status[service_name] = False
            return False

service_health = ServiceHealth()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and log requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(
        "Request processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        client_ip=request.client.host if request.client else None
    )
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.observe(process_time)
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/services/health")
async def services_health():
    """Check health of all services"""
    health_results = {}
    
    for service_name, service_url in SERVICES.items():
        is_healthy = await service_health.check_service_health(service_name, service_url)
        health_results[service_name] = {
            "healthy": is_healthy,
            "url": service_url
        }
    
    return {
        "timestamp": time.time(),
        "services": health_results,
        "overall_health": all(result["healthy"] for result in health_results.values())
    }

# Rate limiting middleware
async def check_rate_limit(request: Request):
    """Simple rate limiting using Redis"""
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"
    
    # Get current request count
    current_count = redis_client.get(key)
    if current_count is None:
        current_count = 0
    else:
        current_count = int(current_count)
    
    # Check if limit exceeded (100 requests per minute)
    if current_count >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Increment counter
    redis_client.incr(key)
    redis_client.expire(key, 60)  # Expire after 1 minute

# Service routing
@app.post("/api/speech/transcribe")
async def route_speech_transcribe(request: Request):
    """Route speech transcription requests to speech service"""
    await check_rate_limit(request)
    
    try:
        body = await request.json()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SERVICES['speech']}/transcribe",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error("Speech service error", status_code=response.status_code, response=response.text)
                raise HTTPException(status_code=response.status_code, detail="Speech service error")
            
            return response.json()
            
    except httpx.TimeoutException:
        logger.error("Speech service timeout")
        raise HTTPException(status_code=504, detail="Speech service timeout")
    except Exception as e:
        logger.error("Speech service error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/code/generate")
async def route_code_generate(request: Request):
    """Route code generation requests to code service"""
    await check_rate_limit(request)
    
    try:
        body = await request.json()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SERVICES['code']}/generate",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error("Code service error", status_code=response.status_code, response=response.text)
                raise HTTPException(status_code=response.status_code, detail="Code service error")
            
            return response.json()
            
    except httpx.TimeoutException:
        logger.error("Code service timeout")
        raise HTTPException(status_code=504, detail="Code service timeout")
    except Exception as e:
        logger.error("Code service error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/weather/{location}")
async def route_weather(request: Request, location: str):
    """Route weather requests to weather service"""
    await check_rate_limit(request)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SERVICES['weather']}/weather/{location}",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error("Weather service error", status_code=response.status_code, response=response.text)
                raise HTTPException(status_code=response.status_code, detail="Weather service error")
            
            return response.json()
            
    except httpx.TimeoutException:
        logger.error("Weather service timeout")
        raise HTTPException(status_code=504, detail="Weather service timeout")
    except Exception as e:
        logger.error("Weather service error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/tasks")
async def route_task_create(request: Request):
    """Route task creation requests to task service"""
    await check_rate_limit(request)
    
    try:
        body = await request.json()
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{SERVICES['task']}/tasks",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error("Task service error", status_code=response.status_code, response=response.text)
                raise HTTPException(status_code=response.status_code, detail="Task service error")
            
            return response.json()
            
    except httpx.TimeoutException:
        logger.error("Task service timeout")
        raise HTTPException(status_code=504, detail="Task service timeout")
    except Exception as e:
        logger.error("Task service error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/login")
async def route_auth_login(request: Request):
    """Route authentication requests to user service"""
    await check_rate_limit(request)
    
    try:
        body = await request.json()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{SERVICES['user']}/auth/login",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error("User service error", status_code=response.status_code, response=response.text)
                raise HTTPException(status_code=response.status_code, detail="Authentication failed")
            
            return response.json()
            
    except httpx.TimeoutException:
        logger.error("User service timeout")
        raise HTTPException(status_code=504, detail="User service timeout")
    except Exception as e:
        logger.error("User service error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 