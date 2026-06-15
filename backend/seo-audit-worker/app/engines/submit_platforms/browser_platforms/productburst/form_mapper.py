from __future__ import annotations

import re
from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.token_extractor import TokenExtractor

from .selectors import (
    PRODUCTBURST_CATEGORY_SELECTORS,
    PRODUCTBURST_CREATORS_SEARCH_SELECTORS,
    PRODUCTBURST_DESCRIPTION_SELECTORS,
    PRODUCTBURST_FIRST_COMMENT_SELECTORS,
    PRODUCTBURST_LAUNCH_WEEK_SELECTORS,
    PRODUCTBURST_LAUNCH_BUTTON_SELECTORS,
    PRODUCTBURST_LIVE_WEBSITE_SELECTORS,
    PRODUCTBURST_LOGO_UPLOAD_SELECTORS,
    PRODUCTBURST_PREVIEW_TOGGLE_SELECTORS,
    PRODUCTBURST_PRODUCT_TYPE_SELECTORS,
    PRODUCTBURST_STACK_SELECTORS,
    PRODUCTBURST_STARTUP_NAME_SELECTORS,
    PRODUCTBURST_TAGLINE_SELECTORS,
)


class ProductBurstFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler
        self.browser_helper: BrowserAutomationHelper | None = None

    def bind_browser_helper(self, browser_helper: BrowserAutomationHelper) -> None:
        self.browser_helper = browser_helper

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        return {
            "startup_name": metadata.get("SiteName") or metadata.get("StartupName") or "My Product",
            "website_url": metadata.get("WebsiteUrl") or url,
            "tagline": metadata.get("Tagline") or metadata.get("ShortDescription") or metadata.get("Description") or "",
            "product_description": metadata.get("ProductDescription") or metadata.get("Description") or "",
            "categories": metadata.get("Categories") or metadata.get("Keywords") or "",
            "stacks": metadata.get("Stacks") or "",
            "product_type": metadata.get("ProductType") or "",
            "launch_plan": metadata.get("LaunchPlan") or "Launch",
            "launch_week": metadata.get("LaunchWeek") or "",
            "creators": metadata.get("Creators") or "",
            "launchpad_url": metadata.get("LaunchpadUrl") or "",
            "launchpad_id": metadata.get("LaunchpadId") or "",
            "enable_preview": metadata.get("EnablePreLaunchPreview") or "true",
            "create_first_comment": metadata.get("CreateFirstComment") or "false",
            "logo": metadata.get("Logo") or "",
        }

    def _normalize_csv(self, value: str) -> str:
        parts = [part.strip() for part in re.split(r"[;,]", value or "") if part.strip()]
        return "; ".join(parts)

    async def _fill_contenteditable(self, page, value: str) -> bool:
        if not value:
            return False

        locator = page.locator("div[contenteditable='true']")
        if await locator.count() == 0:
            return False

        try:
            target = locator.first
            if await target.is_visible():
                await target.click()
                await target.fill(value)
                return True
        except Exception:
            try:
                await locator.first.evaluate(
                    """(el, value) => {
                        el.focus();
                        el.textContent = value;
                        el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: value }));
                    }""",
                    value,
                )
                return True
            except Exception:
                return False

        return False

    async def _select_by_text(self, page, candidates: list[str], value: str) -> bool:
        if not value:
            return False

        normalized_candidates = [part.strip() for part in re.split(r"[;,]", value) if part.strip()]
        if not normalized_candidates:
            normalized_candidates = [value.strip()]

        for candidate in normalized_candidates:
            for selector in candidates:
                locator = page.locator(selector)
                if await locator.count() == 0:
                    continue
                try:
                    target = locator.first
                    if not await target.is_visible():
                        continue
                    tag_name = await target.evaluate("(el) => el.tagName.toLowerCase()")
                    if tag_name == "select":
                        options = await target.locator("option").all_inner_texts()
                        if any(candidate.lower() in (opt or "").lower() for opt in options):
                            await target.select_option(label=candidate)
                            return True
                    else:
                        await target.click()
                        await page.keyboard.type(candidate)
                        await page.keyboard.press("Enter")
                        return True
                except Exception:
                    continue

        return False

    async def extract_form_data(self, page) -> Dict[str, str]:
        extractor = TokenExtractor(page)
        return {
            "startup_name": await extractor.extract_input_value(PRODUCTBURST_STARTUP_NAME_SELECTORS),
            "website_url": await extractor.extract_input_value(PRODUCTBURST_LIVE_WEBSITE_SELECTORS),
            "tagline": await extractor.extract_input_value(PRODUCTBURST_TAGLINE_SELECTORS),
            "product_description": await extractor.extract_text(PRODUCTBURST_DESCRIPTION_SELECTORS),
            "categories": await extractor.extract_input_value(PRODUCTBURST_CATEGORY_SELECTORS),
            "stacks": await extractor.extract_input_value(PRODUCTBURST_STACK_SELECTORS),
            "product_type": await extractor.extract_input_value(PRODUCTBURST_PRODUCT_TYPE_SELECTORS),
            "launch_week": await extractor.extract_input_value(PRODUCTBURST_LAUNCH_WEEK_SELECTORS),
            "creators": await extractor.extract_input_value(PRODUCTBURST_CREATORS_SEARCH_SELECTORS),
            "logo": await extractor.extract_input_value(PRODUCTBURST_LOGO_UPLOAD_SELECTORS),
        }

    def normalize_extracted_data(self, extracted: Dict[str, str], defaults: Dict[str, str]) -> Dict[str, str]:
        normalized = dict(extracted)
        for key, default_key in [
            ("startup_name", "startup_name"),
            ("website_url", "website_url"),
            ("tagline", "tagline"),
            ("product_description", "product_description"),
            ("categories", "categories"),
            ("stacks", "stacks"),
            ("product_type", "product_type"),
            ("launch_week", "launch_week"),
            ("creators", "creators"),
            ("logo", "logo"),
        ]:
            if not (normalized.get(key) or "").strip():
                normalized[key] = defaults[default_key]
        return normalized

    async def fill_prelaunch_form(self, page, browser_helper: BrowserAutomationHelper, data: Dict[str, str]) -> None:
        await browser_helper.fill_first_visible(page, PRODUCTBURST_STARTUP_NAME_SELECTORS, data.get("startup_name", ""))
        await browser_helper.fill_first_visible(page, PRODUCTBURST_LIVE_WEBSITE_SELECTORS, data.get("website_url", ""))
        await browser_helper.fill_first_visible(page, PRODUCTBURST_TAGLINE_SELECTORS, data.get("tagline", ""))

        description = data.get("product_description", "")
        if description and not await browser_helper.fill_first_visible(page, PRODUCTBURST_DESCRIPTION_SELECTORS, description):
            await self._fill_contenteditable(page, description)

        await self._select_by_text(page, PRODUCTBURST_CATEGORY_SELECTORS, self._normalize_csv(data.get("categories", "")))
        await self._select_by_text(page, PRODUCTBURST_STACK_SELECTORS, self._normalize_csv(data.get("stacks", "")))
        await self._select_by_text(page, PRODUCTBURST_PRODUCT_TYPE_SELECTORS, data.get("product_type", ""))
        await self._select_by_text(page, PRODUCTBURST_LAUNCH_WEEK_SELECTORS, data.get("launch_week", ""))
        await self._select_by_text(page, PRODUCTBURST_CREATORS_SEARCH_SELECTORS, data.get("creators", ""))

        if data.get("enable_preview", "").lower() in {"true", "1", "yes", "on"}:
            await browser_helper.click_first_visible(page, PRODUCTBURST_PREVIEW_TOGGLE_SELECTORS)

        if data.get("create_first_comment", "").lower() in {"true", "1", "yes", "on"}:
            await browser_helper.click_first_visible(page, PRODUCTBURST_FIRST_COMMENT_SELECTORS)

    def extract_launchpad_id(self, current_url: str) -> str:
        match = re.search(r"/launchpad/([A-Za-z0-9x]+)", current_url or "")
        return match.group(1) if match else ""

