from __future__ import annotations

from typing import Any, Optional


class TokenExtractor:
    def __init__(self, page):
        self.page = page

    async def extract_input_value(self, selectors: list[str]) -> str:
        for selector in selectors:
            locator = self.page.locator(selector)
            if await locator.count() == 0:
                continue
            try:
                if await locator.first.is_visible():
                    return (await locator.first.input_value()).strip()
            except Exception:
                continue
        return ""

    async def extract_text(self, selectors: list[str]) -> str:
        for selector in selectors:
            locator = self.page.locator(selector)
            if await locator.count() == 0:
                continue
            try:
                if await locator.first.is_visible():
                    return (await locator.first.text_content() or "").strip()
            except Exception:
                continue
        return ""
