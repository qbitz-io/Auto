"""File Guardian - prevents Auto from modifying its own core files without human approval."""
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# Core files that define Auto's identity and architecture.
# Modifying these requires human approval.
PROTECTED_PATHS = [
    # Core system
    "backend/core/config.py",
    "backend/core/state.py",
    "backend/core/build_loop.py",
    "backend/core/llm.py",
    "backend/core/file_guardian.py",
    # Agents
    "backend/agents/orchestrator.py",
    "backend/agents/planner.py",
    "backend/agents/builder.py",
    "backend/agents/validator.py",
    "backend/agents/toolsmith.py",
    "backend/agents/self_improver.py",
    # Tools
    "backend/tools/base_tools.py",
    "backend/tools/self_improver_tools.py",
    # API
    "backend/api.py",
    # Entry point
    "backend/main.py",
    # Frontend core
    "frontend/app/layout.tsx",
    "frontend/app/page.tsx",
    "frontend/next.config.ts",
    "frontend/package.json",
    "frontend/tsconfig.json",
    # Frontend components (locked after working)
    "frontend/components/ChatInterface.tsx",
    "frontend/components/StatusPanel.tsx",
    "frontend/components/CapabilitiesPanel.tsx",
    "frontend/components/BuildStepsPanel.tsx",
    "frontend/components/ControlPanel.tsx",
]

# Paths that are always blocked, even with approval
FORBIDDEN_PATHS = [
    ".env",
    ".env.local",
    ".git/",
]


class PendingApproval(BaseModel):
    """A queued file write awaiting human approval."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    file_path: str
    content: str
    reason: str = ""
    requested_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending"  # pending, approved, denied
    reviewed_at: Optional[datetime] = None


class FileGuardian:
    """Guards protected files from unauthorized modification."""

    def __init__(self):
        self._approvals: Dict[str, PendingApproval] = {}
        self._lock = asyncio.Lock()

    def is_protected(self, file_path: str) -> bool:
        """Check if a file path is protected."""
        normalized = file_path.replace("\\", "/").lstrip("/")
        for protected in PROTECTED_PATHS:
            if normalized == protected or normalized.endswith("/" + protected):
                return True
        return False

    def is_forbidden(self, file_path: str) -> bool:
        """Check if a file path is always forbidden."""
        normalized = file_path.replace("\\", "/").lstrip("/")
        for forbidden in FORBIDDEN_PATHS:
            if normalized == forbidden or normalized.startswith(forbidden):
                return True
        return False

    async def request_approval(self, file_path: str, content: str, reason: str = "") -> PendingApproval:
        """Queue a write for human approval. Returns the pending approval."""
        async with self._lock:
            approval = PendingApproval(
                file_path=file_path,
                content=content,
                reason=reason,
            )
            self._approvals[approval.id] = approval
            return approval

    async def get_pending(self) -> List[PendingApproval]:
        """Get all pending approvals."""
        async with self._lock:
            return [a for a in self._approvals.values() if a.status == "pending"]

    async def get_all(self) -> List[PendingApproval]:
        """Get all approvals (any status)."""
        async with self._lock:
            return list(self._approvals.values())

    async def get_approval(self, approval_id: str) -> Optional[PendingApproval]:
        """Get a specific approval by ID."""
        async with self._lock:
            return self._approvals.get(approval_id)

    async def approve(self, approval_id: str) -> Optional[PendingApproval]:
        """Approve a pending write. Returns the approval if found."""
        async with self._lock:
            approval = self._approvals.get(approval_id)
            if approval and approval.status == "pending":
                approval.status = "approved"
                approval.reviewed_at = datetime.now()
                return approval
            return None

    async def deny(self, approval_id: str) -> Optional[PendingApproval]:
        """Deny a pending write. Returns the approval if found."""
        async with self._lock:
            approval = self._approvals.get(approval_id)
            if approval and approval.status == "pending":
                approval.status = "denied"
                approval.reviewed_at = datetime.now()
                return approval
            return None

    async def clear_resolved(self) -> int:
        """Remove all approved/denied entries. Returns count removed."""
        async with self._lock:
            resolved = [k for k, v in self._approvals.items() if v.status != "pending"]
            for k in resolved:
                del self._approvals[k]
            return len(resolved)


# Global instance
file_guardian = FileGuardian()
