"""FastAPI server for frontend communication."""
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core import state_manager, build_loop, settings
from backend.core.file_guardian import file_guardian
from backend.agents import orchestrator


# Create FastAPI app
app = FastAPI(
    title="Self-Building LangChain System API",
    description="API for monitoring and controlling the self-building system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class BuildRequest(BaseModel):
    """Request to trigger a build."""
    force: bool = False


class TaskRequest(BaseModel):
    """Request to execute a task."""
    task: str
    context: Dict[str, Any] = {}


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Self-Building LangChain System",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/api/state")
async def get_state():
    """Get current system state."""
    state = await state_manager.get_state()
    return state.model_dump(mode='json')


@app.get("/api/capabilities")
async def get_capabilities():
    """Get system capabilities."""
    state = await state_manager.get_state()
    return {
        "capabilities": [cap.model_dump() for cap in state.capabilities],
        "total": len(state.capabilities),
        "implemented": sum(1 for c in state.capabilities if c.implemented),
    }


@app.get("/api/build-steps")
async def get_build_steps(limit: int = 50):
    """Get recent build steps."""
    state = await state_manager.get_state()
    steps = state.build_steps[-limit:] if len(state.build_steps) > limit else state.build_steps
    return {
        "steps": [step.model_dump(mode='json') for step in reversed(steps)],
        "total": len(state.build_steps),
    }


@app.get("/api/files")
async def get_generated_files():
    """Get list of generated files."""
    state = await state_manager.get_state()
    return {
        "files": state.generated_files,
        "count": len(state.generated_files),
    }


@app.post("/api/build")
async def trigger_build(request: BuildRequest):
    """Trigger a build cycle."""
    if build_loop.running:
        raise HTTPException(status_code=409, detail="Build loop is already running")
    
    # Run build loop in background
    asyncio.create_task(build_loop.run())
    
    return {
        "status": "started",
        "message": "Build loop started"
    }


@app.post("/api/build/stop")
async def stop_build():
    """Stop the build loop."""
    if not build_loop.running:
        raise HTTPException(status_code=409, detail="Build loop is not running")
    
    build_loop.stop()
    
    return {
        "status": "stopped",
        "message": "Build loop stopped"
    }


@app.post("/api/task")
async def execute_task(request: TaskRequest):
    """Execute a task with the orchestrator."""
    try:
        result = await orchestrator.run(request.task, request.context)
        return {
            "status": "completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Get current system status."""
    state = await state_manager.get_state()
    
    return {
        "build_loop_running": build_loop.running,
        "build_loop_iteration": build_loop.iteration,
        "total_capabilities": len(state.capabilities),
        "implemented_capabilities": sum(1 for c in state.capabilities if c.implemented),
        "total_files": len(state.generated_files),
        "total_steps": len(state.build_steps),
        "last_updated": state.last_updated.isoformat() if state.last_updated else None,
    }


# --- File Guardian: Human-in-the-loop approval endpoints ---

@app.get("/api/approvals")
async def list_approvals(status: str = "pending"):
    """List file write approvals. Filter by status: pending, approved, denied, or all."""
    if status == "all":
        approvals = await file_guardian.get_all()
    elif status == "pending":
        approvals = await file_guardian.get_pending()
    else:
        all_approvals = await file_guardian.get_all()
        approvals = [a for a in all_approvals if a.status == status]

    return {
        "approvals": [a.model_dump(mode="json") for a in approvals],
        "count": len(approvals),
    }


@app.get("/api/approvals/{approval_id}")
async def get_approval(approval_id: str):
    """Get details of a specific approval including the proposed file content."""
    approval = await file_guardian.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval.model_dump(mode="json")


@app.post("/api/approvals/{approval_id}/approve")
async def approve_write(approval_id: str):
    """Approve a pending file write. This will execute the write."""
    approval = await file_guardian.approve(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found or already resolved")

    # Execute the approved write
    full_path = settings.project_root / approval.file_path
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(approval.content)
        await state_manager.add_generated_file(approval.file_path)
        return {
            "status": "approved_and_written",
            "file_path": approval.file_path,
            "message": f"Change to {approval.file_path} has been approved and applied.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approved but write failed: {str(e)}")


@app.post("/api/approvals/{approval_id}/deny")
async def deny_write(approval_id: str):
    """Deny a pending file write. The change will be discarded."""
    approval = await file_guardian.deny(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found or already resolved")
    return {
        "status": "denied",
        "file_path": approval.file_path,
        "message": f"Change to {approval.file_path} has been denied.",
    }


@app.get("/api/protected-files")
async def list_protected_files():
    """List all protected file paths."""
    from backend.core.file_guardian import PROTECTED_PATHS, FORBIDDEN_PATHS
    return {
        "protected": PROTECTED_PATHS,
        "forbidden": FORBIDDEN_PATHS,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        state = await state_manager.get_state()
        await websocket.send_json({
            "type": "state",
            "data": state.model_dump(mode='json')
        })
        
        # Keep connection alive and send updates
        while True:
            # Wait for messages (ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send periodic updates
                state = await state_manager.get_state()
                await websocket.send_json({
                    "type": "state_update",
                    "data": {
                        "build_loop_running": build_loop.running,
                        "iteration": build_loop.iteration,
                        "timestamp": datetime.now().isoformat(),
                    }
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
