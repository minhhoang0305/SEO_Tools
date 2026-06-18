from __future__ import annotations

from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper

from .selectors import (
    NEWAIFORYOU_ADD_PRODUCT_SELECTORS,
    NEWAIFORYOU_SUBMIT_BUTTON_SELECTORS,
    NEWAIFORYOU_TOOL_NAME_SELECTORS,
    NEWAIFORYOU_URL_SELECTORS,
)


class NewAIForYouFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        return {
            "tool_name": (
                metadata.get("SiteName")
                or metadata.get("ToolName")
                or metadata.get("ProductName")
                or metadata.get("SoftwareName")
                or metadata.get("ProjectName")
                or "My Tool"
            ),
            "url": metadata.get("WebsiteUrl") or metadata.get("HomepageUrl") or url,
        }

    async def _fill_exact_name(self, page, field_name: str, value: str) -> bool:
        if not value:
            return False

        locator = page.locator(f"input[name='{field_name}'], textarea[name='{field_name}']")
        try:
            count = await locator.count()
        except Exception:
            count = 0

        for index in range(count):
            target = locator.nth(index)
            try:
                if not await target.is_visible():
                    continue
                await target.scroll_into_view_if_needed(timeout=2000)
                await target.fill(value)
                return True
            except Exception:
                continue
        return False

    async def _fill_by_label_or_placeholder(self, page, labels: list[str], value: str) -> bool:
        if not value:
            return False

        for label in labels:
            try:
                field = page.get_by_label(label, exact=False)
                if await field.count() > 0 and await field.first.is_visible():
                    await field.first.fill(value)
                    return True
            except Exception:
                pass

            try:
                field = page.get_by_placeholder(label, exact=False)
                if await field.count() > 0 and await field.first.is_visible():
                    await field.first.fill(value)
                    return True
            except Exception:
                pass

        return False

    async def fill_form(self, page, browser_helper: BrowserAutomationHelper | None, data: Dict[str, str]) -> None:
        tool_name = data.get("tool_name", "")
        website_url = data.get("url", "")

        if tool_name and not (
            await self._fill_exact_name(page, "toolname", tool_name)
            or await self._fill_exact_name(page, "tool_name", tool_name)
            or await self._fill_exact_name(page, "toolName", tool_name)
            or await self._fill_by_label_or_placeholder(page, ["Tool name", "Tool Name", "Name"], tool_name)
        ):
            raise ValueError("Không tìm thấy field Tool name của New AI For You.")

        if website_url and not (
            await self._fill_exact_name(page, "url", website_url)
            or await self._fill_exact_name(page, "website_url", website_url)
            or await self._fill_exact_name(page, "websiteUrl", website_url)
            or await self._fill_by_label_or_placeholder(page, ["URL", "Website URL", "Website url"], website_url)
        ):
            raise ValueError("Không tìm thấy field URL của New AI For You.")

    async def click_add_product(self, page, browser_helper: BrowserAutomationHelper) -> bool:
        return await browser_helper.click_first_visible(page, NEWAIFORYOU_ADD_PRODUCT_SELECTORS)

    async def click_submit(self, page, browser_helper: BrowserAutomationHelper) -> bool:
        return await browser_helper.click_first_visible(page, NEWAIFORYOU_SUBMIT_BUTTON_SELECTORS)
