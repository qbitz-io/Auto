"""Base tools for the self-building system."""
import os
import re
import ast
import subprocess
from pathlib import Path
from typing import Optional, List
from langchain_core.tools import tool
from ..core import settings, state_manager
from ..core.file_guardian import file_guardian


# File type routing: extension → allowed directories
# Prevents writing code to the wrong location (e.g. JSX in backend/)
FILE_TYPE_ROUTES = {
    ".py": ["backend/"],
    ".js": ["frontend/", "scripts/"],
    ".jsx": ["frontend/"],
    ".ts": ["frontend/"],
    ".tsx": ["frontend/", "mobile/"],
    ".css": ["frontend/"],
    ".json": ["backend/", "frontend/", "mobile/", "."],
    ".md": ["."],
    ".html": ["frontend/"],
    ".toml": ["."],
    ".txt": ["backend/", "."],
    ".yml": ["."],
    ".yaml": ["."],
}

# Windows reserved filenames that cannot be created
WINDOWS_RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
    "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
}


def _validate_file_path(file_path: str) -> Optional[str]:
    """Validate a file path for safety and correctness.

    Returns an error message if invalid, None if OK.
    """
    normalized = file_path.replace("\\", "/").lstrip("/")

    # Check for Windows reserved names in any path component
    for part in Path(normalized).parts:
        name_without_ext = part.split(".")[0].lower()
        if name_without_ext in WINDOWS_RESERVED_NAMES:
            return f"BLOCKED: '{part}' is a Windows reserved filename and cannot be used."

    # Check file extension routing
    ext = Path(normalized).suffix.lower()
    if ext and ext in FILE_TYPE_ROUTES:
        allowed_dirs = FILE_TYPE_ROUTES[ext]
        in_allowed_dir = False
        for allowed in allowed_dirs:
            if allowed == ".":
                # Root-level files OK if only one path component
                if "/" not in normalized:
                    in_allowed_dir = True
                    break
            elif normalized.startswith(allowed):
                in_allowed_dir = True
                break
        if not in_allowed_dir:
            allowed_list = ", ".join(FILE_TYPE_ROUTES[ext])
            return (
                f"BLOCKED: '{ext}' files should be in [{allowed_list}], "
                f"but '{normalized}' is outside those directories. "
                f"Use the correct directory for this file type."
            )

    return None


@tool
async def read_file(file_path: str) -> str:
    """Read the contents of a file.
    
    Args:
        file_path: Path to the file to read (relative to project root)
    
    Returns:
        File contents as string
    """
    full_path = settings.project_root / file_path
    try:
        with open(full_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
async def write_file(file_path: str, content: str) -> str:
    """Write content to a file, creating directories if needed.

    Protected core files require human approval before they can be modified.
    Forbidden files (.env, .git) are always blocked.

    Args:
        file_path: Path to the file to write (relative to project root)
        content: Content to write to the file

    Returns:
        Success or error message
    """
    # PATH VALIDATION: Check extension/directory routing and reserved names
    path_error = _validate_file_path(file_path)
    if path_error:
        return path_error

    # GUARDIAN CHECK: Block forbidden files entirely
    if file_guardian.is_forbidden(file_path):
        return f"BLOCKED: '{file_path}' is a forbidden path and cannot be written to."

    # GUARDIAN CHECK: Protected files need human approval
    if file_guardian.is_protected(file_path):
        approval = await file_guardian.request_approval(
            file_path=file_path,
            content=content,
            reason=f"Auto attempted to modify protected core file: {file_path}",
        )
        return (
            f"QUEUED FOR APPROVAL: '{file_path}' is a protected core file. "
            f"Change has been queued for human review (approval id: {approval.id}). "
            f"A human must approve this change at /api/approvals/{approval.id}/approve before it takes effect. "
            f"Do NOT attempt to bypass this protection."
        )

    # Non-protected file: write normally
    full_path = settings.project_root / file_path
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)

        # Track generated file
        await state_manager.add_generated_file(file_path)

        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
async def list_directory(directory_path: str = ".") -> str:
    """List contents of a directory.
    
    Args:
        directory_path: Path to directory (relative to project root)
    
    Returns:
        List of files and directories
    """
    full_path = settings.project_root / directory_path
    try:
        items = []
        for item in sorted(full_path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            items.append(f"{item_type}: {item.name}")
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
async def validate_python_syntax(code: str) -> str:
    """Validate Python code syntax.
    
    Args:
        code: Python code to validate
    
    Returns:
        Validation result message
    """
    try:
        ast.parse(code)
        return "Python syntax is valid"
    except SyntaxError as e:
        return f"Syntax error: {str(e)}"


@tool
async def run_command(command: str, cwd: Optional[str] = None) -> str:
    """Run a shell command and return output.
    
    Args:
        command: Command to run
        cwd: Working directory (relative to project root)
    
    Returns:
        Command output or error
    """
    # Sanitize: replace redirects to Windows reserved names (e.g. "> nul")
    # with /dev/null equivalent for the current platform
    sanitized = re.sub(
        r'>\s*(?:' + '|'.join(WINDOWS_RESERVED_NAMES) + r')\b',
        '> /dev/null',
        command,
        flags=re.IGNORECASE,
    )

    work_dir = settings.project_root / cwd if cwd else settings.project_root
    try:
        result = subprocess.run(
            sanitized,
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return f"Exit code: {result.returncode}\n{output}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except Exception as e:
        return f"Error running command: {str(e)}"


@tool
async def get_system_state() -> str:
    """Get current system state including capabilities and build history.
    
    Returns:
        JSON representation of system state
    """
    state = await state_manager.get_state()
    return state.model_dump_json(indent=2)


@tool
async def check_file_exists(file_path: str) -> str:
    """Check if a file exists.
    
    Args:
        file_path: Path to check (relative to project root)
    
    Returns:
        "exists" or "not found"
    """
    full_path = settings.project_root / file_path
    return "exists" if full_path.exists() else "not found"


# Export all tools as a list
BASE_TOOLS = [
    read_file,
    write_file,
    list_directory,
    validate_python_syntax,
    run_command,
    get_system_state,
    check_file_exists,
]
