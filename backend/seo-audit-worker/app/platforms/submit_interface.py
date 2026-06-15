from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class SubmitHandlerInterface(ABC):
    @abstractmethod
    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        raise NotImplementedError
