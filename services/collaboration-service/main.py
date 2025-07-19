from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uuid
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections and sessions
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Dict] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id

    async def connect(self, websocket: WebSocket, user_id: str, session_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = session_id
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "users": [],
                "code": "",
                "language": "python",
                "created_at": datetime.now().isoformat()
            }
        
        if user_id not in self.sessions[session_id]["users"]:
            self.sessions[session_id]["users"].append(user_id)
        
        # Notify others in session
        await self.broadcast_to_session(session_id, {
            "type": "user_joined",
            "user_id": user_id,
            "users": self.sessions[session_id]["users"],
            "code": self.sessions[session_id]["code"]
        }, exclude_user=user_id)

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        session_id = self.user_sessions.get(user_id)
        if session_id and session_id in self.sessions:
            if user_id in self.sessions[session_id]["users"]:
                self.sessions[session_id]["users"].remove(user_id)
            
            # Clean up empty sessions
            if not self.sessions[session_id]["users"]:
                del self.sessions[session_id]
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

    async def broadcast_to_session(self, session_id: str, message: dict, exclude_user: str = None):
        if session_id not in self.sessions:
            return
        
        for user_id in self.sessions[session_id]["users"]:
            if user_id != exclude_user and user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(json.dumps(message))
                except:
                    # Remove dead connection
                    self.disconnect(user_id)

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "collaboration-service"}

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    if session_id not in manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "users": manager.sessions[session_id]["users"],
        "code": manager.sessions[session_id]["code"],
        "language": manager.sessions[session_id]["language"],
        "created_at": manager.sessions[session_id]["created_at"]
    }

@app.post("/sessions")
async def create_session():
    session_id = str(uuid.uuid4())[:8]
    manager.sessions[session_id] = {
        "users": [],
        "code": "",
        "language": "python",
        "created_at": datetime.now().isoformat()
    }
    return {"session_id": session_id}

@app.websocket("/ws/{session_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str):
    await manager.connect(websocket, user_id, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "code_update":
                # Update code in session
                manager.sessions[session_id]["code"] = message["code"]
                manager.sessions[session_id]["language"] = message.get("language", "python")
                
                # Broadcast to other users in session
                await manager.broadcast_to_session(session_id, {
                    "type": "code_update",
                    "code": message["code"],
                    "language": message.get("language", "python"),
                    "user_id": user_id
                }, exclude_user=user_id)
            
            elif message["type"] == "cursor_update":
                # Broadcast cursor position
                await manager.broadcast_to_session(session_id, {
                    "type": "cursor_update",
                    "user_id": user_id,
                    "position": message["position"]
                }, exclude_user=user_id)
            
            elif message["type"] == "voice_command":
                # Handle voice commands in collaboration
                await manager.broadcast_to_session(session_id, {
                    "type": "voice_command",
                    "user_id": user_id,
                    "command": message["command"]
                })
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        # Notify others that user left
        session_id = manager.user_sessions.get(user_id)
        if session_id:
            await manager.broadcast_to_session(session_id, {
                "type": "user_left",
                "user_id": user_id,
                "users": manager.sessions[session_id]["users"]
            })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 