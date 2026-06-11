from __future__ import annotations

import json
from typing import Any, Dict, Optional


class ResultParser:
    def parse_json(self, raw: Any, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if raw is None:
            return default or {}

        if isinstance(raw, dict):
            return raw

        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", errors="ignore")

        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                return parsed if isinstance(parsed, dict) else {"value": parsed}
            except Exception:
                return default or {"value": raw}

        return default or {"value": raw}

    def contains_any(self, haystack: str, needles: list[str]) -> bool:
        normalized = (haystack or "").lower()
        return any(needle.lower() in normalized for needle in needles)
