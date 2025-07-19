from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime
import uuid

app = FastAPI(title="Live AI Coding Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class CodeGenerationRequest(BaseModel):
    voice_command: str
    language: str
    context: Optional[str] = None
    user_id: str

class CodeGenerationResponse(BaseModel):
    code: str
    explanation: str
    language: str
    timestamp: datetime
    suggestions: List[str]

class CollaborationMessage(BaseModel):
    user_id: str
    username: str
    message_type: str  # "code_change", "comment", "cursor_move"
    content: Dict
    timestamp: datetime

# In-memory storage (in production, use Redis/Database)
active_sessions: Dict[str, Dict] = {}
connected_clients: Dict[str, List[WebSocket]] = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "live-ai-coding"}

@app.post("/api/live-coding/generate", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate code based on voice command"""
    try:
        # Simulate AI code generation based on command and language
        code, explanation, suggestions = await generate_ai_code(
            request.voice_command, 
            request.language, 
            request.context
        )
        
        return CodeGenerationResponse(
            code=code,
            explanation=explanation,
            language=request.language,
            timestamp=datetime.now(),
            suggestions=suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/live-coding/session/create")
async def create_session(session_name: str, user_id: str):
    """Create a new collaborative coding session"""
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "id": session_id,
        "name": session_name,
        "created_by": user_id,
        "created_at": datetime.now(),
        "participants": [user_id],
        "code": "",
        "language": "javascript",
        "comments": []
    }
    connected_clients[session_id] = []
    return {"session_id": session_id, "session": active_sessions[session_id]}

@app.get("/api/live-coding/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return active_sessions[session_id]

@app.websocket("/ws/live-coding/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await websocket.accept()
    
    if session_id not in connected_clients:
        connected_clients[session_id] = []
    
    connected_clients[session_id].append(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            await handle_collaboration_message(session_id, message, websocket)
            
    except WebSocketDisconnect:
        # Remove client from connected list
        if session_id in connected_clients:
            connected_clients[session_id].remove(websocket)
        print(f"Client disconnected from session {session_id}")

async def handle_collaboration_message(session_id: str, message: Dict, sender_websocket: WebSocket):
    """Handle real-time collaboration messages"""
    message_type = message.get("type")
    
    if message_type == "code_change":
        # Update session code
        if session_id in active_sessions:
            active_sessions[session_id]["code"] = message.get("code", "")
            active_sessions[session_id]["language"] = message.get("language", "javascript")
        
        # Broadcast to all other clients
        await broadcast_message(session_id, message, exclude_websocket=sender_websocket)
    
    elif message_type == "comment":
        # Add comment to session
        if session_id in active_sessions:
            comment = {
                "id": str(uuid.uuid4()),
                "user_id": message.get("user_id"),
                "username": message.get("username"),
                "line": message.get("line"),
                "text": message.get("text"),
                "timestamp": datetime.now().isoformat()
            }
            active_sessions[session_id]["comments"].append(comment)
        
        # Broadcast to all clients
        await broadcast_message(session_id, message, exclude_websocket=sender_websocket)
    
    elif message_type == "cursor_move":
        # Broadcast cursor position to other clients
        await broadcast_message(session_id, message, exclude_websocket=sender_websocket)
    
    elif message_type == "user_join":
        # Add user to session participants
        if session_id in active_sessions:
            user_id = message.get("user_id")
            if user_id not in active_sessions[session_id]["participants"]:
                active_sessions[session_id]["participants"].append(user_id)
        
        # Broadcast to all clients
        await broadcast_message(session_id, message, exclude_websocket=sender_websocket)

async def broadcast_message(session_id: str, message: Dict, exclude_websocket: WebSocket = None):
    """Broadcast message to all connected clients in a session"""
    if session_id in connected_clients:
        for websocket in connected_clients[session_id]:
            if websocket != exclude_websocket:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    # Remove disconnected websocket
                    connected_clients[session_id].remove(websocket)

async def generate_ai_code(voice_command: str, language: str, context: str = None) -> tuple:
    """Generate code using AI (simulated)"""
    command_lower = voice_command.lower()
    
    if language == "javascript":
        if "function" in command_lower or "create" in command_lower:
            if "todo" in command_lower:
                code = """function addTodo(text) {
  const todo = {
    id: Date.now(),
    text: text,
    completed: false,
    createdAt: new Date()
  };
  
  return todo;
}

// Usage example
const newTodo = addTodo("Buy groceries");
console.log(newTodo);"""
                explanation = "Created a function to add new todo items with unique IDs and timestamps"
                suggestions = ["Add validation for empty text", "Include priority levels", "Add due date support"]
            else:
                code = """function processData(data) {
  // Validate input
  if (!Array.isArray(data)) {
    throw new Error('Input must be an array');
  }
  
  // Process each item
  return data.map(item => ({
    ...item,
    processed: true,
    processedAt: new Date()
  }));
}

// Usage example
const data = [{ id: 1, name: 'Item 1' }];
const processed = processData(data);
console.log(processed);"""
                explanation = "Created a data processing function with input validation and transformation"
                suggestions = ["Add error handling", "Include data filtering", "Add performance optimization"]
        
        elif "react" in command_lower or "component" in command_lower:
            code = """import React, { useState, useEffect } from 'react';

const TodoList = () => {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const addTodo = () => {
    if (input.trim()) {
      const newTodo = {
        id: Date.now(),
        text: input.trim(),
        completed: false
      };
      setTodos([...todos, newTodo]);
      setInput('');
    }
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  return (
    <div className="todo-container">
      <h1>Todo List</h1>
      <div className="input-section">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="Add new todo..."
          className="todo-input"
        />
        <button onClick={addTodo} className="add-button">
          Add Todo
        </button>
      </div>
      <ul className="todo-list">
        {todos.map(todo => (
          <li 
            key={todo.id} 
            onClick={() => toggleTodo(todo.id)}
            className={\`todo-item \${todo.completed ? 'completed' : ''}\`}
          >
            {todo.text}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TodoList;"""
            explanation = "Created a complete React todo component with state management and user interactions"
            suggestions = ["Add local storage persistence", "Include delete functionality", "Add categories/tags"]
    
    elif language == "python":
        if "function" in command_lower or "create" in command_lower:
            if "process" in command_lower:
                code = """def process_data(data):
    \"\"\"
    Process the given dataset with validation and error handling
    \"\"\"
    if not isinstance(data, list):
        raise ValueError("Data must be a list")
    
    if not data:
        return []
    
    processed_data = []
    for item in data:
        try:
            processed_item = {
                'id': item.get('id', len(processed_data) + 1),
                'name': str(item.get('name', 'Unknown')),
                'processed': True,
                'processed_at': datetime.now().isoformat()
            }
            processed_data.append(processed_item)
        except Exception as e:
            print(f"Error processing item {item}: {e}")
            continue
    
    return processed_data

# Example usage
from datetime import datetime

data = [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}]
result = process_data(data)
print(result)"""
                explanation = "Created a robust data processing function with validation and error handling"
                suggestions = ["Add data type validation", "Include logging", "Add performance metrics"]
            else:
                code = """def calculate_statistics(numbers):
    \"\"\"
    Calculate basic statistics for a list of numbers
    \"\"\"
    if not numbers:
        return {
            'count': 0,
            'sum': 0,
            'mean': 0,
            'min': None,
            'max': None
        }
    
    return {
        'count': len(numbers),
        'sum': sum(numbers),
        'mean': sum(numbers) / len(numbers),
        'min': min(numbers),
        'max': max(numbers)
    }

# Example usage
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
stats = calculate_statistics(numbers)
print(f"Statistics: {stats}")"""
                explanation = "Created a statistics calculation function with comprehensive metrics"
                suggestions = ["Add median calculation", "Include standard deviation", "Add outlier detection"]
    
    else:
        # Default response for other languages
        code = f"""// Generated code for: "{voice_command}"
// Language: {language}
// TODO: Implement the requested functionality

console.log("Hello from AI-generated code!");"""
        explanation = f"Generated placeholder code for {language} based on your request"
        suggestions = ["Implement the specific functionality", "Add error handling", "Include documentation"]
    
    return code, explanation, suggestions

@app.get("/api/live-coding/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "sessions": [
            {
                "id": session_id,
                "name": session["name"],
                "participants_count": len(session["participants"]),
                "created_at": session["created_at"]
            }
            for session_id, session in active_sessions.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005) 