# backend/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.speech import SpeechProcessor
from app.code_generator import CodeGenerator

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    processor = SpeechProcessor()
    code_gen = CodeGenerator()

    try:
        while True:
            data = await websocket.receive_bytes()

            # Extract audio data (skip 4-byte header)
            audio_data = data[4:] if len(data) > 4 else data

            # Debug audio properties
            print(f"Received audio chunk: {len(audio_data)} bytes")

            text = await processor.transcribe_stream(audio_data)
            await websocket.send_text(f"TRANSCRIPT:{text}")

            if len(text.strip()) > 3 and not text.startswith("["):
                code = code_gen.generate_code(text)
                await websocket.send_text(f"CODE:{code}")

    except Exception as e:
        print(f"WebSocket error: {str(e)}")