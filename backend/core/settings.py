import os
from pathlib import Path

# Project root directory
project_root = Path(__file__).parent.parent

# Memory directory for persistent state
memory_dir = project_root / "backend" / "memory"
memory_dir.mkdir(parents=True, exist_ok=True)

# API server host and port
api_host = os.getenv("API_HOST", "0.0.0.0")
api_port = int(os.getenv("PORT", os.getenv("API_PORT", 8080)))

# Other settings can be added here
