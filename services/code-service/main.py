from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import JSONResponse
import time
import os
from code_generator import CodeGenerator

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
CODE_GENERATION_REQUESTS = Counter('code_generation_requests_total', 'Total code generation requests')
CODE_GENERATION_DURATION = Histogram('code_generation_duration_seconds', 'Code generation processing time')
CODE_GENERATION_ERRORS = Counter('code_generation_errors_total', 'Total code generation errors')

app = FastAPI(
    title="CodeVoice Code Generation Service",
    description="Microservice for AI-powered code generation",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    prompt: str
    language: str = "python"
    context: str = ""
    style: str = "clean"

class CodeResponse(BaseModel):
    code: str
    language: str
    duration: float
    tokens_used: int = 0

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "code-service"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/generate", response_model=CodeResponse)
async def generate_code(request: CodeRequest):
    """Generate code based on natural language prompt"""
    start_time = time.time()
    CODE_GENERATION_REQUESTS.inc()
    
    try:
        logger.info("🤖 Received code generation request", 
                   language=request.language,
                   prompt_length=len(request.prompt))
        
        # Initialize code generator
        code_gen = CodeGenerator()
        
        # Generate code
        code = code_gen.generate_code(request.prompt, request.language)
        
        if code.startswith("# Error generating"):
            CODE_GENERATION_ERRORS.inc()
            logger.error("❌ Code generation failed", error=code)
            raise HTTPException(status_code=400, detail=f"Code generation failed: {code}")
        
        # Calculate processing time
        duration = time.time() - start_time
        CODE_GENERATION_DURATION.observe(duration)
        
        logger.info("✅ Code generation completed", 
                   language=request.language,
                   code_length=len(code),
                   duration_seconds=duration)
        
        return CodeResponse(
            code=code,
            language=request.language,
            duration=duration,
            tokens_used=len(code.split())  # Rough estimate
        )
        
    except Exception as e:
        CODE_GENERATION_ERRORS.inc()
        logger.error("❌ Error generating code", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/batch")
async def generate_code_batch(code_requests: list[CodeRequest]):
    """Generate multiple code snippets in batch"""
    start_time = time.time()
    
    try:
        logger.info("🤖 Received batch code generation request", 
                   batch_size=len(code_requests))
        
        code_gen = CodeGenerator()
        results = []
        
        for i, request in enumerate(code_requests):
            try:
                code = code_gen.generate_code(request.prompt, request.language)
                
                results.append({
                    "index": i,
                    "code": code,
                    "success": not code.startswith("# Error generating"),
                    "language": request.language,
                    "prompt": request.prompt
                })
                
            except Exception as e:
                logger.error(f"❌ Error generating code {i}", error=str(e))
                results.append({
                    "index": i,
                    "code": "",
                    "success": False,
                    "error": str(e),
                    "language": request.language,
                    "prompt": request.prompt
                })
        
        duration = time.time() - start_time
        
        logger.info("✅ Batch code generation completed", 
                   batch_size=len(code_requests),
                   duration_seconds=duration)
        
        return {
            "results": results,
            "total_duration": duration,
            "successful_generations": sum(1 for r in results if r["success"])
        }
        
    except Exception as e:
        logger.error("❌ Error processing batch", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "languages": [
            {"id": "python", "name": "Python", "icon": "🐍"},
            {"id": "javascript", "name": "JavaScript", "icon": "🟨"},
            {"id": "typescript", "name": "TypeScript", "icon": "🔷"},
            {"id": "java", "name": "Java", "icon": "☕"},
            {"id": "cpp", "name": "C++", "icon": "⚡"},
            {"id": "csharp", "name": "C#", "icon": "💎"},
            {"id": "go", "name": "Go", "icon": "🐹"},
            {"id": "rust", "name": "Rust", "icon": "🦀"},
            {"id": "php", "name": "PHP", "icon": "🐘"},
            {"id": "ruby", "name": "Ruby", "icon": "💎"},
            {"id": "swift", "name": "Swift", "icon": "🍎"},
            {"id": "kotlin", "name": "Kotlin", "icon": "🟦"}
        ]
    }

@app.get("/styles")
async def get_code_styles():
    """Get available code generation styles"""
    return {
        "styles": [
            {"id": "clean", "name": "Clean and Simple", "description": "Minimal, readable code"},
            {"id": "detailed", "name": "Detailed", "description": "Comprehensive with comments"},
            {"id": "optimized", "name": "Optimized", "description": "Performance-focused code"},
            {"id": "enterprise", "name": "Enterprise", "description": "Production-ready with error handling"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 