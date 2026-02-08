import uuid
from fastapi import APIRouter, HTTPException
from backend.agents import sandbox_manager, flyio_agent

router = APIRouter()

# In-memory store for user instances and API keys
user_instances = {}

@router.post("/launch")
async def launch_instance(user_id: str):
    """Launch a new Fly.io instance for a user and generate API key."""
    # Generate API key
    api_key = str(uuid.uuid4())

    # Spawn instance using sandbox_manager
    branch = "main"
    repo_url = "https://github.com/example/repo.git"

    instance_id = await sandbox_manager.spawn_instance(branch=branch, repo_url=repo_url)

    user_instances[user_id] = {
        "instance_id": instance_id,
        "api_key": api_key,
    }

    return {
        "instance_id": instance_id,
        "api_key": api_key,
        "message": "Instance launched successfully",
    }

@router.get("/instance/{user_id}")
async def get_instance_info(user_id: str):
    info = user_instances.get(user_id)
    if not info:
        raise HTTPException(status_code=404, detail="User instance not found")
    return info
