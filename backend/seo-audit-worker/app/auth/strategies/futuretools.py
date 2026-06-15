from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.auth.base import BaseAuthStrategy
from app.session.storage_state_store import FileStorageStateStore


DEFAULT_STORAGE_STATE_PATH = os.getenv(
    "FUTURETOOLS_STORAGE_STATE_PATH",
    str(Path(__file__).resolve().parents[3] / ".playwright" / "futuretools_storage_state.json"),
)
DEFAULT_PROFILE_DIR = os.getenv(
    "FUTURETOOLS_PROFILE_DIR",
    str(Path(__file__).resolve().parents[3] / ".playwright" / "futuretools_chrome_profile"),
)


class FutureToolsAuthStrategy(BaseAuthStrategy):
    def __init__(self, handler: Any):
        super().__init__(handler)
        self.session_store = FileStorageStateStore(DEFAULT_STORAGE_STATE_PATH)
        self.profile_dir = Path(DEFAULT_PROFILE_DIR)

    async def ensure_authenticated(self, browser):
        context_kwargs = self.session_store.context_kwargs()
        context_kwargs.setdefault("viewport", {"width": 1280, "height": 900})
        context_kwargs.setdefault(
            "user_agent",
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        if self.profile_dir.exists():
            context_kwargs.setdefault("storage_state", str(self.session_store.storage_state_path))
        return await browser.new_context(**context_kwargs)
