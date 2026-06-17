from __future__ import annotations

import re
from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper


class BAItoolsFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        return {
            "tool_name": metadata.get("SiteName") or metadata.get("ToolName") or metadata.get("AItoolName") or "My AI Tool",
            "website_url": metadata.get("WebsiteUrl") or metadata.get("HomepageUrl") or url,
            "plan_index": str(metadata.get("BAIToolsPlanIndex") or metadata.get("planIndex") or 0),
            "locale": metadata.get("BAIToolsLocale") or metadata.get("locale") or "en",
        }

    async def fill_form(self, page, browser_helper: BrowserAutomationHelper, data: Dict[str, str]) -> None:
        tool_name = data.get("tool_name", "")
        website_url = data.get("website_url", "")

        if tool_name:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='name of your AI Tools']",
                    "input[placeholder*='AI Tool Name']",
                    "input[name='tool_name']",
                    "input[name='toolName']",
                    "input[type='text']",
                ],
                tool_name,
            )

        if website_url:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='website']",
                    "input[placeholder*='URL']",
                    "input[name='website_url']",
                    "input[name='websiteUrl']",
                    "input[type='url']",
                ],
                website_url,
            )

        submit_buttons = [
            "button:has-text('Submit')",
            "button[type='submit']",
            "input[type='submit']",
        ]
        await browser_helper.click_first_visible(page, submit_buttons)
