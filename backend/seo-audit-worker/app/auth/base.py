from abc import ABC, abstractmethod
from typing import Any

from app.session.storage_state_store import FileStorageStateStore


class BaseAuthStrategy(ABC):
    def __init__(self, handler: Any):
        self.handler = handler
        self.platform_info = handler.platform_info
        self.session_store = FileStorageStateStore()

    @abstractmethod
    async def ensure_authenticated(self, browser):
        raise NotImplementedError
