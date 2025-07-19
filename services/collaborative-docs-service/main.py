from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime
import uuid
import difflib

app = FastAPI(title="Collaborative Documents Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Document(BaseModel):
    id: str
    title: str
    content: str
    language: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    collaborators: List[str]
    version: int

class Comment(BaseModel):
    id: str
    document_id: str
    line: int
    text: str
    user_id: str
    username: str
    timestamp: datetime
    resolved: bool

class DocumentChange(BaseModel):
    document_id: str
    user_id: str
    username: str
    change_type: str  # "content", "comment", "cursor"
    content: Dict
    timestamp: datetime

# In-memory storage (in production, use Redis/Database)
documents: Dict[str, Document] = {}
comments: Dict[str, List[Comment]] = {}
document_versions: Dict[str, List[Dict]] = {}
connected_clients: Dict[str, List[WebSocket]] = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "collaborative-docs"}

@app.post("/api/documents/create")
async def create_document(title: str, language: str, user_id: str, username: str):
    """Create a new collaborative document"""
    doc_id = str(uuid.uuid4())
    
    document = Document(
        id=doc_id,
        title=title,
        content="// Start coding here...",
        language=language,
        created_by=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        collaborators=[user_id],
        version=1
    )
    
    documents[doc_id] = document
    comments[doc_id] = []
    document_versions[doc_id] = [{
        "version": 1,
        "content": document.content,
        "timestamp": datetime.now(),
        "user_id": user_id
    }]
    connected_clients[doc_id] = []
    
    return {"document": document, "message": "Document created successfully"}

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get document details and content"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[doc_id]
    doc_comments = comments.get(doc_id, [])
    
    return {
        "document": doc,
        "comments": doc_comments,
        "collaborators_count": len(doc.collaborators)
    }

@app.get("/api/documents")
async def list_documents():
    """List all documents"""
    return {
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "language": doc.language,
                "created_by": doc.created_by,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at,
                "collaborators_count": len(doc.collaborators),
                "version": doc.version
            }
            for doc in documents.values()
        ]
    }

@app.post("/api/documents/{doc_id}/update")
async def update_document(doc_id: str, content: str, user_id: str):
    """Update document content"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[doc_id]
    old_content = doc.content
    
    # Update document
    doc.content = content
    doc.updated_at = datetime.now()
    doc.version += 1
    
    # Store version history
    document_versions[doc_id].append({
        "version": doc.version,
        "content": content,
        "timestamp": datetime.now(),
        "user_id": user_id
    })
    
    # Generate diff
    diff = list(difflib.unified_diff(
        old_content.splitlines(keepends=True),
        content.splitlines(keepends=True),
        fromfile='Previous version',
        tofile='Current version'
    ))
    
    return {
        "document": doc,
        "diff": ''.join(diff),
        "message": "Document updated successfully"
    }

@app.post("/api/documents/{doc_id}/comment")
async def add_comment(doc_id: str, line: int, text: str, user_id: str, username: str):
    """Add a comment to a specific line"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    comment = Comment(
        id=str(uuid.uuid4()),
        document_id=doc_id,
        line=line,
        text=text,
        user_id=user_id,
        username=username,
        timestamp=datetime.now(),
        resolved=False
    )
    
    if doc_id not in comments:
        comments[doc_id] = []
    
    comments[doc_id].append(comment)
    
    return {"comment": comment, "message": "Comment added successfully"}

@app.put("/api/documents/{doc_id}/comment/{comment_id}/resolve")
async def resolve_comment(doc_id: str, comment_id: str):
    """Mark a comment as resolved"""
    if doc_id not in comments:
        raise HTTPException(status_code=404, detail="Document not found")
    
    for comment in comments[doc_id]:
        if comment.id == comment_id:
            comment.resolved = True
            return {"message": "Comment resolved successfully"}
    
    raise HTTPException(status_code=404, detail="Comment not found")

@app.get("/api/documents/{doc_id}/versions")
async def get_document_versions(doc_id: str):
    """Get version history of a document"""
    if doc_id not in document_versions:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"versions": document_versions[doc_id]}

@app.post("/api/documents/{doc_id}/restore/{version}")
async def restore_version(doc_id: str, version: int, user_id: str):
    """Restore document to a specific version"""
    if doc_id not in document_versions:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Find the version
    target_version = None
    for v in document_versions[doc_id]:
        if v["version"] == version:
            target_version = v
            break
    
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Restore the document
    doc = documents[doc_id]
    doc.content = target_version["content"]
    doc.updated_at = datetime.now()
    doc.version += 1
    
    # Add new version entry
    document_versions[doc_id].append({
        "version": doc.version,
        "content": doc.content,
        "timestamp": datetime.now(),
        "user_id": user_id,
        "restored_from": version
    })
    
    return {"document": doc, "message": f"Document restored to version {version}"}

@app.websocket("/ws/documents/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await websocket.accept()
    
    if doc_id not in connected_clients:
        connected_clients[doc_id] = []
    
    connected_clients[doc_id].append(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            await handle_collaboration_message(doc_id, message, websocket)
            
    except WebSocketDisconnect:
        # Remove client from connected list
        if doc_id in connected_clients:
            connected_clients[doc_id].remove(websocket)
        print(f"Client disconnected from document {doc_id}")

async def handle_collaboration_message(doc_id: str, message: Dict, sender_websocket: WebSocket):
    """Handle real-time collaboration messages"""
    message_type = message.get("type")
    
    if message_type == "content_change":
        # Update document content
        if doc_id in documents:
            doc = documents[doc_id]
            doc.content = message.get("content", "")
            doc.updated_at = datetime.now()
            doc.version += 1
            
            # Store version
            document_versions[doc_id].append({
                "version": doc.version,
                "content": doc.content,
                "timestamp": datetime.now(),
                "user_id": message.get("user_id")
            })
        
        # Broadcast to all other clients
        await broadcast_message(doc_id, message, exclude_websocket=sender_websocket)
    
    elif message_type == "comment_add":
        # Add comment
        comment_data = message.get("comment", {})
        comment = Comment(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            line=comment_data.get("line"),
            text=comment_data.get("text"),
            user_id=message.get("user_id"),
            username=message.get("username"),
            timestamp=datetime.now(),
            resolved=False
        )
        
        if doc_id not in comments:
            comments[doc_id] = []
        comments[doc_id].append(comment)
        
        # Broadcast to all clients
        await broadcast_message(doc_id, message, exclude_websocket=sender_websocket)
    
    elif message_type == "cursor_move":
        # Broadcast cursor position to other clients
        await broadcast_message(doc_id, message, exclude_websocket=sender_websocket)
    
    elif message_type == "user_join":
        # Add user to document collaborators
        if doc_id in documents:
            user_id = message.get("user_id")
            if user_id not in documents[doc_id].collaborators:
                documents[doc_id].collaborators.append(user_id)
        
        # Broadcast to all clients
        await broadcast_message(doc_id, message, exclude_websocket=sender_websocket)
    
    elif message_type == "user_typing":
        # Broadcast typing indicator
        await broadcast_message(doc_id, message, exclude_websocket=sender_websocket)

async def broadcast_message(doc_id: str, message: Dict, exclude_websocket: WebSocket = None):
    """Broadcast message to all connected clients in a document"""
    if doc_id in connected_clients:
        for websocket in connected_clients[doc_id]:
            if websocket != exclude_websocket:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    # Remove disconnected websocket
                    connected_clients[doc_id].remove(websocket)

@app.get("/api/documents/{doc_id}/comments")
async def get_document_comments(doc_id: str):
    """Get all comments for a document"""
    if doc_id not in comments:
        return {"comments": []}
    
    return {"comments": comments[doc_id]}

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str, user_id: str):
    """Delete a document (only creator can delete)"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[doc_id]
    if doc.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only document creator can delete")
    
    # Clean up
    del documents[doc_id]
    if doc_id in comments:
        del comments[doc_id]
    if doc_id in document_versions:
        del document_versions[doc_id]
    if doc_id in connected_clients:
        del connected_clients[doc_id]
    
    return {"message": "Document deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 