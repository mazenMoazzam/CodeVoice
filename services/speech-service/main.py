from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import io
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import JSONResponse
import time
import os
from speech_processor import SpeechProcessor

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
TRANSCRIPTION_REQUESTS = Counter('transcription_requests_total', 'Total transcription requests')
TRANSCRIPTION_DURATION = Histogram('transcription_duration_seconds', 'Transcription processing time')
TRANSCRIPTION_ERRORS = Counter('transcription_errors_total', 'Total transcription errors')

app = FastAPI(
    title="CodeVoice Speech Service",
    description="Microservice for audio transcription and speech processing",
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

class AudioRequest(BaseModel):
    audio_data: str
    audio_format: str = "webm"
    language: str = "en"

class TranscriptionResponse(BaseModel):
    transcript: str
    confidence: float
    duration: float
    language: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "speech-service"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: AudioRequest):
    """Transcribe audio data to text"""
    start_time = time.time()
    TRANSCRIPTION_REQUESTS.inc()
    
    try:
        logger.info("🎵 Received transcription request", 
                   audio_format=request.audio_format, 
                   language=request.language)
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)
        logger.info("📦 Decoded audio", size_bytes=len(audio_bytes))
        
        # Initialize speech processor
        processor = SpeechProcessor()
        
        # Transcribe audio
        transcript = await processor.transcribe_audio(audio_bytes, request.audio_format)
        
        if not transcript or transcript.startswith("[ERROR"):
            TRANSCRIPTION_ERRORS.inc()
            logger.error("❌ Transcription failed", transcript=transcript)
            raise HTTPException(status_code=400, detail=f"Transcription failed: {transcript}")
        
        # Calculate processing time
        duration = time.time() - start_time
        TRANSCRIPTION_DURATION.observe(duration)
        
        logger.info("✅ Transcription completed", 
                   transcript_length=len(transcript),
                   duration_seconds=duration)
        
        return TranscriptionResponse(
            transcript=transcript,
            confidence=0.95,  # Placeholder - could be enhanced with actual confidence scores
            duration=duration,
            language=request.language
        )
        
    except Exception as e:
        TRANSCRIPTION_ERRORS.inc()
        logger.error("❌ Error processing audio", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/batch")
async def transcribe_batch(audio_requests: list[AudioRequest]):
    """Transcribe multiple audio files in batch"""
    start_time = time.time()
    
    try:
        logger.info("🎵 Received batch transcription request", 
                   batch_size=len(audio_requests))
        
        processor = SpeechProcessor()
        results = []
        
        for i, request in enumerate(audio_requests):
            try:
                audio_bytes = base64.b64decode(request.audio_data)
                transcript = await processor.transcribe_audio(audio_bytes, request.audio_format)
                
                results.append({
                    "index": i,
                    "transcript": transcript,
                    "success": not transcript.startswith("[ERROR"),
                    "language": request.language
                })
                
            except Exception as e:
                logger.error(f"❌ Error processing audio {i}", error=str(e))
                results.append({
                    "index": i,
                    "transcript": "",
                    "success": False,
                    "error": str(e),
                    "language": request.language
                })
        
        duration = time.time() - start_time
        
        logger.info("✅ Batch transcription completed", 
                   batch_size=len(audio_requests),
                   duration_seconds=duration)
        
        return {
            "results": results,
            "total_duration": duration,
            "successful_transcriptions": sum(1 for r in results if r["success"])
        }
        
    except Exception as e:
        logger.error("❌ Error processing batch", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 