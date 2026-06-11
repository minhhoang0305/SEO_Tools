from __future__ import annotations

import time
from typing import Dict

from .constants import STACKSHARE_COOLDOWN_PATTERNS


class StackShareCooldownDetector:
    async def _get_visible_page_text(self, page) -> str:
        try:
            body = page.locator("body")
            if await body.count() == 0:
                return ""
            return (await body.first.inner_text(timeout=3000)).strip().lower()
        except Exception:
            return ""

    async def _get_visible_dialog_text(self, page) -> str:
        try:
            dialog = page.locator("[role='dialog']")
            if await dialog.count() == 0:
                return ""
            return (await dialog.first.inner_text(timeout=3000)).strip().lower()
        except Exception:
            return ""

    def _extract_cooldown_hint(self, text: str) -> Dict[str, str]:
        normalized = (text or "").strip().lower()
        if not normalized:
            return {}

        for pattern in STACKSHARE_COOLDOWN_PATTERNS:
            import re

            match = re.search(pattern, normalized, flags=re.IGNORECASE)
            if not match:
                continue

            remaining = match.groupdict().get("remaining") or match.groupdict().get("window") or ""
            return {
                "pattern": pattern,
                "remaining_hours": remaining,
                "matched_text": match.group(0),
            }

        return {}

    async def detect(self, page) -> Dict[str, str]:
        dialog_text = await self._get_visible_dialog_text(page)
        if dialog_text:
            hint = self._extract_cooldown_hint(dialog_text)
            if hint:
                hint["source"] = "dialog"
                return hint

        page_text = await self._get_visible_page_text(page)
        if not page_text:
            return {}

        hint = self._extract_cooldown_hint(page_text)
        if hint:
            hint["source"] = "page"
        return hint

    async def wait_for_crawl_or_cooldown(self, page, timeout_ms: int = 5000) -> Dict[str, str]:
        deadline = time.time() + (timeout_ms / 1000)
        while time.time() < deadline:
            cooldown_hint = await self.detect(page)
            if cooldown_hint:
                return cooldown_hint

            await page.wait_for_timeout(500)

        return {}
