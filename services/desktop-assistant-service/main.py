from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Desktop Assistant Service", description="Processes voice commands for desktop automation.", version="0.1.0")

class VoiceCommandRequest(BaseModel):
    command: str
    user_id: Optional[str] = None
    timestamp: Optional[str] = None

class ActionResponse(BaseModel):
    action: str
    description: str
    details: Optional[dict] = None

@app.post("/api/desktop/command", response_model=ActionResponse)
async def process_voice_command(request: VoiceCommandRequest):
    # Stub: parse command and return a sample action
    if "youtube" in request.command.lower():
        return ActionResponse(
            action="browser_search",
            description=f"Searching YouTube for: {request.command}",
            details={"url": "https://youtube.com/results", "query": request.command}
        )
    elif "calendar" in request.command.lower() or "meeting" in request.command.lower():
        return ActionResponse(
            action="calendar_book",
            description="Booking a meeting (stub)",
            details={}
        )
    elif "email" in request.command.lower():
        return ActionResponse(
            action="email_compose",
            description="Composing an email (stub)",
            details={}
        )
    else:
        return ActionResponse(
            action="unknown",
            description="Command not recognized.",
            details={}
        ) 