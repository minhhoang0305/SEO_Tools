from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


DEFAULT_BROWSER_CONTEXT = {
    "viewport": {"width": 1280, "height": 800},
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


@dataclass(slots=True)
class BrowserAutomationHelper:
    browser: Any
    context_options: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_BROWSER_CONTEXT))

    async def new_context(self, **overrides):
        options = {**self.context_options, **overrides}
        return await self.browser.new_context(**options)

    async def new_page(self, context):
        return await context.new_page()

    async def goto(self, page, url: str, *, wait_until: str = "networkidle", timeout: int = 30000):
        await page.goto(url, wait_until=wait_until, timeout=timeout)

    async def fill_first_visible(self, page, selectors, value: str) -> bool:
        if not value:
            return False

        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue

            target = locator.first
            try:
                if await target.is_visible():
                    await target.fill(value)
                    return True
            except Exception:
                continue

        return False

    async def read_first_visible(self, page, selectors) -> str:
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue

            target = locator.first
            try:
                if await target.is_visible():
                    tag_name = await target.evaluate("(el) => el.tagName.toLowerCase()")
                    if tag_name in ["input", "textarea"]:
                        return (await target.input_value()).strip()
                    return (await target.text_content() or "").strip()
            except Exception:
                continue

        return ""

    async def click_first_visible(self, page, selectors) -> bool:
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue

            target = locator.first
            try:
                if await target.is_visible():
                    await target.click()
                    return True
            except Exception:
                continue

        return False

    async def wait_for_button_enabled(self, page, selector: str, text: str, timeout: int = 30000) -> None:
        await page.wait_for_function(
            """({ selector, text }) => {
                const btn = Array.from(document.querySelectorAll(selector))
                    .find(el => (el.textContent || '').includes(text));
                return btn && !btn.disabled;
            }""",
            arg={"selector": selector, "text": text},
            timeout=timeout,
        )

    async def wait_for_text_visible(self, page, selector: str, text: str, timeout: int = 30000) -> None:
        await page.wait_for_function(
            """({ selector, text }) => {
                const el = Array.from(document.querySelectorAll(selector))
                    .find(node => (node.textContent || '').includes(text));
                return !!el;
            }""",
            arg={"selector": selector, "text": text},
            timeout=timeout,
        )

    async def close_context(self, context) -> None:
        if context is not None:
            await context.close()

    async def close_browser(self) -> None:
        if self.browser is not None:
            await self.browser.close()
