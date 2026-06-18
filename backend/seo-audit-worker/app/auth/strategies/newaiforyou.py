from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.auth.base import BaseAuthStrategy
from app.session.storage_state_store import FileStorageStateStore


DEFAULT_STORAGE_STATE_PATH = os.getenv(
    "NEWAIFORYOU_STORAGE_STATE_PATH",
    str(Path(__file__).resolve().parents[3] / ".playwright" / "newaiforyou_storage_state.json"),
)


class NewAIForYouAuthStrategy(BaseAuthStrategy):
    def __init__(self, handler: Any):
        super().__init__(handler)
        self.session_store = FileStorageStateStore(DEFAULT_STORAGE_STATE_PATH)

    async def ensure_authenticated(self, browser):
        if not self.session_store.exists():
            raise ValueError("Chưa có storage_state của New AI For You. Hãy login Google OAuth local và lưu session trước.")

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
        return await browser.new_context(**context_kwargs)
