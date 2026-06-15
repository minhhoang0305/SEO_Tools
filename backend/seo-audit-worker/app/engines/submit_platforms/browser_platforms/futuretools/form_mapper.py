from __future__ import annotations

import re
from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper

from .constants import FUTURETOOLS_CATEGORY_OPTIONS, FUTURETOOLS_PRICING_OPTIONS


class FutureToolsFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        your_name = (
            metadata.get("YourName")
            or metadata.get("SubmitterName")
            or metadata.get("SiteName")
            or "Jane Doe"
        )
        tool_name = metadata.get("ToolName") or metadata.get("SiteName") or "My AI Tool"
        short_description = (
            metadata.get("ShortDescription")
            or metadata.get("Description")
            or "An AI tool worth checking out."
        )
        category = metadata.get("Category") or metadata.get("Categories") or "Productivity"
        pricing = metadata.get("Pricing") or "Free"
        email = metadata.get("ContactEmail") or metadata.get("Email") or ""
        newsletter = metadata.get("NewsletterOptIn") or "false"

        return {
            "your_name": your_name,
            "tool_name": tool_name,
            "tool_url": url,
            "short_description": short_description,
            "category": category,
            "pricing": pricing,
            "email": email,
            "newsletter": newsletter,
        }

    def _resolve_category(self, value: str, tool_name: str, short_description: str) -> str:
        candidate = (value or "").strip()
        if candidate:
            for option in FUTURETOOLS_CATEGORY_OPTIONS:
                if candidate.lower() == option.lower():
                    return option

        haystack = f"{tool_name} {short_description} {candidate}".lower()
        keyword_map = [
            (("chat", "assistant", "bot"), "Chat"),
            (("video", "movie", "clip"), "Generative Video"),
            (("code", "dev", "developer", "program"), "Generative Code"),
            (("voice", "audio", "speech", "tts"), "Text-To-Speech"),
            (("search", "finder", "discover"), "Search Engines"),
            (("design", "logo", "image", "art"), "Design"),
            (("write", "writer", "copy"), "Writing"),
            (("market", "seo", "growth"), "Marketing"),
            (("research", "data", "insight"), "Research"),
        ]

        for keywords, option in keyword_map:
            if any(keyword in haystack for keyword in keywords):
                return option

        return "Productivity"

    def _resolve_pricing(self, value: str) -> str:
        candidate = (value or "").strip()
        for option in FUTURETOOLS_PRICING_OPTIONS:
            if candidate.lower() == option.lower():
                return option
        return "Free"

    async def fill_form(self, page, browser_helper: BrowserAutomationHelper, data: Dict[str, str]) -> None:
        your_name = data.get("your_name", "")
        tool_name = data.get("tool_name", "")
        tool_url = data.get("tool_url", "")
        short_description = data.get("short_description", "")
        category = self._resolve_category(data.get("category", ""), tool_name, short_description)
        pricing = self._resolve_pricing(data.get("pricing", ""))
        email = data.get("email", "")

        if your_name:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder='Jane Doe']",
                    "input[name='name']",
                    "input[aria-label*='Your Name']",
                ],
                your_name,
            )

        if tool_name:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='Tool Name']",
                    "input[name='toolName']",
                    "input[name='tool_name']",
                ],
                tool_name,
            )

        if tool_url:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='example.com']",
                    "input[name='url']",
                    "input[type='url']",
                ],
                tool_url,
            )

        if short_description:
            await browser_helper.fill_first_visible(
                page,
                [
                    "textarea[placeholder*='Briefly describe']",
                    "textarea[name='description']",
                ],
                short_description,
            )

        try:
            category_select = page.get_by_label(re.compile(r"Category", re.IGNORECASE))
            if await category_select.count() > 0:
                await category_select.first.select_option(label=category)
        except Exception:
            pass

        try:
            pricing_radio = page.get_by_role("radio", name=re.compile(f"^{re.escape(pricing)}$", re.IGNORECASE))
            if await pricing_radio.count() > 0:
                await pricing_radio.first.check()
        except Exception:
            try:
                await page.get_by_label(pricing, exact=False).click()
            except Exception:
                pass

        if email:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='you@example.com']",
                    "input[name='email']",
                    "input[type='email']",
                ],
                email,
            )

        newsletter_value = (data.get("newsletter", "") or "").strip().lower()
        if newsletter_value in {"true", "1", "yes", "on"}:
            try:
                newsletter = page.get_by_role(
                    "checkbox",
                    name=re.compile(r"Join the Future Tools newsletter", re.IGNORECASE),
                )
                if await newsletter.count() > 0:
                    await newsletter.first.check()
            except Exception:
                pass
