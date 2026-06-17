from __future__ import annotations

import re
from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper


class TenWordsFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        return {
            "project_name": metadata.get("SiteName") or metadata.get("ProjectName") or metadata.get("ToolName") or "My Project",
            "description": metadata.get("Description") or metadata.get("ShortDescription") or "Describe your project in 10 words or less!",
            "project_url": metadata.get("WebsiteUrl") or metadata.get("HomepageUrl") or url,
            "twitter_handle": metadata.get("TwitterHandle") or metadata.get("XHandle") or "",
            "category": metadata.get("TenWordsCategory") or metadata.get("Category") or "Website",
            "newsletter": metadata.get("TenWordsNewsletter") or metadata.get("NewsletterOptIn") or "No thanks",
        }

    async def fill_form(self, page, browser_helper: BrowserAutomationHelper, data: Dict[str, str]) -> None:
        project_name = data.get("project_name", "")
        description = data.get("description", "")
        project_url = data.get("project_url", "")
        twitter_handle = data.get("twitter_handle", "")
        category = (data.get("category") or "Website").strip()
        newsletter = (data.get("newsletter") or "No thanks").strip()

        if project_name:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='Enter the name of your project']",
                    "input[type='text']",
                    "input[name='projectName']",
                    "input[name='name']",
                ],
                project_name,
            )

        if description:
            await browser_helper.fill_first_visible(
                page,
                [
                    "textarea[placeholder*='Describe your project']",
                    "textarea",
                    "textarea[name='description']",
                ],
                description,
            )

        if project_url:
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='full link']",
                    "input[name='projectUrl']",
                    "input[type='url']",
                    "input[type='text']",
                ],
                project_url,
            )

        if twitter_handle:
            twitter_handle = twitter_handle.lstrip("@").strip()
            await browser_helper.fill_first_visible(
                page,
                [
                    "input[placeholder*='Twitter']",
                    "input[name='twitter']",
                    "input[type='text']",
                ],
                twitter_handle,
            )

        category_map = {
            "Mobile App": "push-app",
            "Website": "push-website",
            "SaaS": "push-saas",
            "Newsletter": "push-newsletter",
            "Other": "push-other",
        }
        category_id = category_map.get(category, "push-website")
        try:
            await page.locator(f"input#{category_id}").check()
        except Exception:
            try:
                await page.get_by_label(re.compile(category, re.IGNORECASE)).check()
            except Exception:
                pass

        newsletter_map = {
            "Daily": "newsletter-daily",
            "Daily (Mon-Thu)": "newsletter-daily",
            "Weekly": "newsletter-weekly",
            "Weekly Digest": "newsletter-weekly",
            "No thanks": "newsletter-none",
        }
        newsletter_id = newsletter_map.get(newsletter, "newsletter-none")
        try:
            await page.locator(f"input#{newsletter_id}").check()
        except Exception:
            try:
                await page.get_by_label(re.compile(newsletter, re.IGNORECASE)).check()
            except Exception:
                pass

        submit_selectors = [
            "button.btn-primary:has-text('Submit Project')",
            "button:has-text('Submit Project')",
            "button[type='button']",
            "text=Submit Project",
        ]
        for selector in submit_selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue
            try:
                target = locator.first
                await target.scroll_into_view_if_needed(timeout=2000)
                await target.click(no_wait_after=True)
                break
            except Exception:
                continue
