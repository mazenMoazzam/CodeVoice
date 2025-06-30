# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import io
from app.speech import SpeechProcessor
from app.code_generator import CodeGenerator

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AudioRequest(BaseModel):
    audio_data: str  
    audio_format: str = "webm"
    language: str = "python"  

@app.post("/transcribe")
async def transcribe_audio(request: AudioRequest):
    try:
        print("🎵 Received transcription request")
        print(f"🔤 Language preference: {request.language}")
        
        audio_bytes = base64.b64decode(request.audio_data)
        print(f"📦 Decoded audio size: {len(audio_bytes)} bytes")
        
        processor = SpeechProcessor()
        transcript = await processor.transcribe_audio(audio_bytes, request.audio_format)
        
        if not transcript or transcript.startswith("[ERROR"):
            raise HTTPException(status_code=400, detail=f"Transcription failed: {transcript}")
        
        print(f"📝 Transcript: {transcript}")
        
        code = ""
        if len(transcript.strip()) > 3:
            code_gen = CodeGenerator()
            code = code_gen.generate_code(transcript, request.language)
            print(f"🤖 Generated {request.language} code: {len(code)} characters")
        
        return {
            "transcript": transcript,
            "code": code,
            "language": request.language
        }
        
    except Exception as e:
        print(f"❌ Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    await websocket.send_text("WebSocket endpoint is deprecated. Use /transcribe POST endpoint instead.")