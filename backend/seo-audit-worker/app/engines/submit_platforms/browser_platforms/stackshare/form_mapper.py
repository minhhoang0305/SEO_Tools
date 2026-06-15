from __future__ import annotations

from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.token_extractor import TokenExtractor

from .constants import STACKSHARE_DEFAULT_SENTINELS
from .selectors import (
    STACKSHARE_DESCRIPTION_SELECTORS,
    STACKSHARE_DOCS_URL_SELECTORS,
    STACKSHARE_FEATURES_SELECTORS,
    STACKSHARE_LOGO_SELECTORS,
    STACKSHARE_SHORT_DESCRIPTION_SELECTORS,
    STACKSHARE_TOOL_NAME_SELECTORS,
    STACKSHARE_WEBSITE_INPUT_SELECTORS,
    STACKSHARE_WEBSITE_URL_SELECTORS,
)


class StackShareFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler
        self.browser_helper: BrowserAutomationHelper | None = None

    def bind_browser_helper(self, browser_helper: BrowserAutomationHelper) -> None:
        self.browser_helper = browser_helper

    def build_defaults(self, metadata: Dict[str, Any], url: str, logo_file_path: str) -> Dict[str, str]:
        site_name = metadata.get("SiteName") or "My SEO Tool Site"
        site_description = (
            metadata.get("Description")
            or "A premium online platform for SEO utilities and tracking."
        )
        site_short_description = metadata.get("ShortDescription") or site_description
        docs_url = metadata.get("DocsUrl") or metadata.get("DocumentationUrl") or ""
        features = metadata.get("Features") or metadata.get("Keywords") or ""
        return {
            "site_name": site_name,
            "site_description": site_description,
            "site_short_description": site_short_description,
            "docs_url": docs_url,
            "features": features,
            "logo_file_path": logo_file_path,
            "url": url,
        }

    def _is_valid(self, value: str) -> bool:
        normalized = (value or "").strip().lower()
        if not normalized:
            return False
        return normalized not in STACKSHARE_DEFAULT_SENTINELS

    async def fill_url(self, page, url: str, browser_helper: BrowserAutomationHelper) -> bool:
        return await browser_helper.fill_first_visible(page, STACKSHARE_WEBSITE_INPUT_SELECTORS, url)

    async def _read_modal_text_fields(self, page) -> list[str]:
        dialog = page.locator("[role='dialog']")
        if await dialog.count() == 0:
            return []

        controls = dialog.locator("input:not([type='hidden']):not([type='file']), textarea")
        values: list[str] = []

        try:
            control_count = await controls.count()
        except Exception:
            return []

        for index in range(control_count):
            locator = controls.nth(index)
            try:
                if not await locator.is_visible():
                    continue

                tag_name = await locator.evaluate("(el) => el.tagName.toLowerCase()")
                if tag_name == "input":
                    value = await locator.input_value()
                else:
                    value = await locator.evaluate(
                        """(el) => {
                            if ('value' in el) return el.value || '';
                            return el.innerText || el.textContent || '';
                        }"""
                    )

                values.append((value or "").strip())
            except Exception:
                continue

        return values

    async def extract_crawled_data(self, page) -> Dict[str, str]:
        modal_values = await self._read_modal_text_fields(page)
        if len(modal_values) >= 5:
            crawled = {
                "tool_name": modal_values[0] if len(modal_values) > 0 else "",
                "website_url": modal_values[1] if len(modal_values) > 1 else "",
                "docs_url": modal_values[2] if len(modal_values) > 2 else "",
                "description": modal_values[3] if len(modal_values) > 3 else "",
                "short_description": modal_values[4] if len(modal_values) > 4 else "",
                "features": modal_values[5] if len(modal_values) > 5 else "",
                "logo": "",
            }
            if any(crawled.values()):
                return crawled

        extractor = TokenExtractor(page)
        return {
            "tool_name": await extractor.extract_input_value(STACKSHARE_TOOL_NAME_SELECTORS),
            "website_url": await extractor.extract_input_value(STACKSHARE_WEBSITE_URL_SELECTORS),
            "docs_url": await extractor.extract_input_value(STACKSHARE_DOCS_URL_SELECTORS),
            "description": await extractor.extract_text(STACKSHARE_DESCRIPTION_SELECTORS),
            "short_description": await extractor.extract_text(STACKSHARE_SHORT_DESCRIPTION_SELECTORS),
            "features": await extractor.extract_text(STACKSHARE_FEATURES_SELECTORS),
            "logo": await extractor.extract_input_value(STACKSHARE_LOGO_SELECTORS),
        }

    def normalize_crawled_data(self, crawled: Dict[str, str], defaults: Dict[str, str]) -> Dict[str, str]:
        normalized = dict(crawled)
        if not self._is_valid(normalized.get("tool_name", "")):
            normalized["tool_name"] = defaults["site_name"]
        if not self._is_valid(normalized.get("website_url", "")):
            normalized["website_url"] = defaults["url"]
        if not self._is_valid(normalized.get("docs_url", "")):
            normalized["docs_url"] = defaults["docs_url"]
        if not self._is_valid(normalized.get("description", "")):
            normalized["description"] = defaults["site_description"]
        if not self._is_valid(normalized.get("short_description", "")):
            normalized["short_description"] = defaults["site_short_description"]
        if not self._is_valid(normalized.get("features", "")):
            normalized["features"] = defaults["features"]
        if not self._is_valid(normalized.get("logo", "")):
            normalized["logo"] = defaults["logo_file_path"]
        return normalized

    async def apply_form(self, page, browser_helper: BrowserAutomationHelper, crawled: Dict[str, str]) -> None:
        await browser_helper.fill_first_visible(page, STACKSHARE_TOOL_NAME_SELECTORS, crawled.get("tool_name", ""))
        await browser_helper.fill_first_visible(page, STACKSHARE_WEBSITE_URL_SELECTORS, crawled.get("website_url", ""))
        await browser_helper.fill_first_visible(page, STACKSHARE_DOCS_URL_SELECTORS, crawled.get("docs_url", ""))
        await browser_helper.fill_first_visible(page, STACKSHARE_SHORT_DESCRIPTION_SELECTORS, crawled.get("short_description", ""))
        await browser_helper.fill_first_visible(page, STACKSHARE_DESCRIPTION_SELECTORS, crawled.get("description", ""))
        await browser_helper.fill_first_visible(page, STACKSHARE_FEATURES_SELECTORS, crawled.get("features", ""))
