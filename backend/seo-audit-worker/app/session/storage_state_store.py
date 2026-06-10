import os
from pathlib import Path
from typing import Any, Optional


DEFAULT_STORAGE_STATE_PATH = str(
    Path(__file__).resolve().parents[2]
    / ".playwright"
    / "stackshare_storage_state.json"
)


class FileStorageStateStore:
    def __init__(self, storage_state_path: Optional[str] = None):
        self.storage_state_path = Path(
            storage_state_path
            or os.getenv("STACKSHARE_STORAGE_STATE_PATH", DEFAULT_STORAGE_STATE_PATH).strip()
        )

    def exists(self) -> bool:
        return self.storage_state_path.exists()

    def context_kwargs(self) -> dict[str, Any]:
        if not self.exists():
            return {}
        return {"storage_state": str(self.storage_state_path)}

    async def save(self, context) -> None:
        self.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(self.storage_state_path))
