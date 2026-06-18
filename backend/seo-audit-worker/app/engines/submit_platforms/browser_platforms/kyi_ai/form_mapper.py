from __future__ import annotations

import re
from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper


class KYIAiFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        return {
            "website_name": (
                metadata.get("SiteName")
                or metadata.get("ToolName")
                or metadata.get("SoftwareName")
                or metadata.get("ProjectName")
                or "Kyi AI"
            ),
            "website_url": metadata.get("WebsiteUrl") or metadata.get("HomepageUrl") or url,
            "email": metadata.get("ContactEmail") or metadata.get("Email") or "support@kyi.ai",
        }

    async def _fill_first_visible_match(self, page, selectors, value: str) -> bool:
        if not value:
            return False

        for selector in selectors:
            locator = page.locator(selector)
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

    async def _fill_exact_name(self, page, field_name: str, value: str) -> bool:
        if not value:
            return False

        locator = page.locator(f"input[name='{field_name}']")
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
                try:
                    observed = (await target.input_value()).strip()
                except Exception:
                    observed = ""
                return observed == value or not observed
            except Exception:
                continue

        return False

    async def _fill_by_label(self, page, label_patterns, value: str) -> bool:
        if not value:
            return False

        for pattern in label_patterns:
            try:
                field = page.get_by_label(re.compile(pattern, re.IGNORECASE))
                if await field.count() == 0:
                    continue
                target = field.first
                if not await target.is_visible():
                    continue
                await target.scroll_into_view_if_needed(timeout=2000)
                await target.fill(value)
                return True
            except Exception:
                continue

        return False

    async def _fill_by_placeholder(self, page, placeholder_patterns, value: str) -> bool:
        if not value:
            return False

        for pattern in placeholder_patterns:
            try:
                field = page.get_by_placeholder(re.compile(pattern, re.IGNORECASE))
                if await field.count() == 0:
                    continue
                target = field.first
                if not await target.is_visible():
                    continue
                await target.scroll_into_view_if_needed(timeout=2000)
                await target.fill(value)
                return True
            except Exception:
                continue

        return False

    async def _read_first_visible_value(self, page, selectors) -> str:
        for selector in selectors:
            locator = page.locator(selector)
            try:
                count = await locator.count()
            except Exception:
                count = 0

            for index in range(count):
                target = locator.nth(index)
                try:
                    if not await target.is_visible():
                        continue
                    tag_name = await target.evaluate("(el) => el.tagName.toLowerCase()")
                    if tag_name in {"input", "textarea"}:
                        return (await target.input_value()).strip()
                    return (await target.text_content() or "").strip()
                except Exception:
                    continue

        return ""

    async def fill_form(self, page, browser_helper: BrowserAutomationHelper | None, data: Dict[str, str]) -> None:
        website_name = data.get("website_name", "")
        website_url = data.get("website_url", "")
        email = data.get("email", "")

        if website_name:
            if await self._fill_exact_name(page, "submit_name", website_name):
                filled = True
            else:
                filled = False
            if not filled:
                filled = await self._fill_by_label(
                page,
                [r"Website Name", r"Tool Name", r"Name"],
                website_name,
            )
            if not filled:
                filled = await self._fill_by_placeholder(
                    page,
                    [r"Website Name", r"Tool Name", r"Name"],
                    website_name,
                )
            if not filled:
                filled = await self._fill_first_visible_match(
                    page,
                    [
                        "input[name='submit_name']",
                        "input#\\:R5svepvcva\\:-form-item",
                        "input[name='name']",
                        "input[name='websiteName']",
                        "input[type='text']",
                    ],
                    website_name,
                )
            if not filled:
                raise ValueError("Không tìm thấy field Website Name của Kyi AI.")

        if website_url:
            filled = await self._fill_exact_name(page, "submit_url", website_url)
            if not filled:
                filled = await self._fill_by_label(
                page,
                [r"Website URL", r"URL"],
                website_url,
            )
            if not filled:
                filled = await self._fill_by_placeholder(
                    page,
                    [r"Website URL", r"URL"],
                    website_url,
                )
            if not filled:
                filled = await self._fill_first_visible_match(
                    page,
                    [
                        "input[name='websiteUrl']",
                        "input[name='url']",
                        "input#\\:R9svepvcva\\:-form-item",
                        "input[type='url']",
                    ],
                    website_url,
                )
            if not filled:
                raise ValueError("Không tìm thấy field Website URL của Kyi AI.")

        if email:
            if await self._fill_exact_name(page, "submit_email", email):
                filled = True
            else:
                filled = False
            if not filled:
                filled = await self._fill_by_label(
                page,
                [r"Your Email", r"Email"],
                email,
            )
            if not filled:
                filled = await self._fill_by_placeholder(
                    page,
                    [r"Your Email", r"Email"],
                    email,
                )
            if not filled:
                filled = await self._fill_first_visible_match(
                    page,
                    [
                        "input[name='email']",
                        "input[name='contactEmail']",
                        "input#\\:Rdsvepvcva\\:-form-item",
                        "input[type='email']",
                    ],
                    email,
                )
            if not filled:
                raise ValueError("Không tìm thấy field Email của Kyi AI.")
    async def click_submit(self, page, browser_helper: BrowserAutomationHelper) -> bool:
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('submit')",
        ]
        return await browser_helper.click_first_visible(page, submit_selectors)
