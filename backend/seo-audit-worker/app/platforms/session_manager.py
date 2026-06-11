from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class LoginSessionManager:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)

    def exists(self) -> bool:
        return self.storage_path.exists()

    async def save(self, context) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(self.storage_path))

    def load_context_options(self) -> Dict[str, Any]:
        if not self.exists():
            return {}
        return {"storage_state": str(self.storage_path)}

    def read_raw(self) -> str:
        if not self.exists():
            return ""
        return self.storage_path.read_text(encoding="utf-8")

    def write_raw(self, raw_json: str) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        normalized = self._normalize(raw_json)
        self.storage_path.write_text(normalized, encoding="utf-8")

    def _normalize(self, raw_json: str) -> str:
        raw = (raw_json or "").strip()
        if not raw:
            return ""

        try:
            parsed = json.loads(raw)
        except Exception:
            return raw

        if isinstance(parsed, list):
            parsed = {"cookies": parsed, "origins": []}
        elif isinstance(parsed, dict):
            parsed.setdefault("cookies", [])
            parsed.setdefault("origins", [])

        return json.dumps(parsed, ensure_ascii=False, indent=2)
