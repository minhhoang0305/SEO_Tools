import os
from pathlib import Path
from typing import Any, Optional

from app.platforms.session_manager import LoginSessionManager


DEFAULT_STORAGE_STATE_PATH = str(
    Path(__file__).resolve().parents[2]
    / ".playwright"
    / "stackshare_storage_state.json"
)


class FileStorageStateStore:
    def __init__(self, storage_state_path: Optional[str] = None):
        self.manager = LoginSessionManager(
            storage_state_path
            or os.getenv("STACKSHARE_STORAGE_STATE_PATH", DEFAULT_STORAGE_STATE_PATH).strip()
        )

    def exists(self) -> bool:
        return self.manager.exists()

    def context_kwargs(self) -> dict[str, Any]:
        return self.manager.load_context_options()

    async def save(self, context) -> None:
        await self.manager.save(context)
