from __future__ import annotations

import re
from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper

from .selectors import (
    AWESOME_INDY_ADD_PRODUCT_SELECTORS,
    AWESOME_INDY_CATEGORIES_SELECTORS,
    AWESOME_INDY_DESCRIPTION_SELECTORS,
    AWESOME_INDY_PRODUCT_NAME_SELECTORS,
    AWESOME_INDY_TAGLINE_SELECTORS,
    AWESOME_INDY_URL_SELECTORS,
    AWESOME_INDY_SUBMIT_BUTTON_SELECTORS,
    AWESOME_INDY_YOUTUBE_SELECTORS,
)


class AwesomeIndieFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        return {
            "product_name": (
                metadata.get("SiteName")
                or metadata.get("ProductName")
                or metadata.get("ToolName")
                or metadata.get("SoftwareName")
                or metadata.get("ProjectName")
                or "My Product"
            ),
            "url": metadata.get("WebsiteUrl") or metadata.get("HomepageUrl") or url,
            "tagline": metadata.get("Tagline") or metadata.get("ShortDescription") or metadata.get("Description") or "",
            "categories": metadata.get("Categories") or metadata.get("Category") or "",
            "description": metadata.get("Description") or metadata.get("FullDescription") or "",
            "social_links": metadata.get("SocialLinks") or "",
            "youtube_video_url": metadata.get("YouTubeVideoUrl") or metadata.get("YoutubeVideoUrl") or "",
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
                    tag_name = await target.evaluate("(el) => el.tagName.toLowerCase()")
                    if tag_name == "select":
                        try:
                            await target.select_option(label=value)
                        except Exception:
                            await target.select_option(value=value)
                    else:
                        await target.fill(value)
                    return True
                except Exception:
                    continue

        return False

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

    def _split_social_links(self, value: str) -> list[str]:
        if not value:
            return []

        parts = [part.strip() for part in re.split(r"[,\n;|]", value) if part.strip()]
        return parts[:5]

    async def _fill_social_links(self, page, value: str) -> bool:
        links = self._split_social_links(value)
        if not links:
            return False

        social_fields = [
            ("socialTwitter", "Twitter"),
            ("socialLinkedIn", "LinkedIn"),
            ("socialGitHub", "GitHub"),
            ("socialFacebook", "Facebook"),
            ("socialInstagram", "Instagram"),
        ]

        filled_any = False

        for index, link in enumerate(links):
            if index >= len(social_fields):
                break

            field_id, placeholder = social_fields[index]
            selectors = [
                f"input#{field_id}",
                f"input[placeholder='{placeholder}']",
                f"input[placeholder*='{placeholder}']",
            ]

            if await self._fill_first_visible_match(page, selectors, link):
                filled_any = True
                continue

            try:
                input_field = page.locator(f"input#{field_id}")
                if await input_field.count() > 0 and await input_field.first.is_visible():
                    await input_field.first.scroll_into_view_if_needed(timeout=2000)
                    await input_field.first.fill(link)
                    filled_any = True
                    continue
            except Exception:
                pass

        return filled_any

    async def _fill_categories(self, page, value: str) -> bool:
        if not value:
            return False

        normalized = [part.strip() for part in re.split(r"[;,]", value) if part.strip()]
        if not normalized:
            normalized = [value.strip()]
        normalized = normalized[:5]

        ant_select_selectors = [
            "div.ant-select.ant-select-multiple",
            "div.ant-select[aria-required='true']",
            "div.ant-select",
            "[role='combobox']",
        ]

        async def _select_category_text(text: str) -> bool:
            for selector in ant_select_selectors:
                locator = page.locator(selector)
                try:
                    if await locator.count() == 0:
                        continue
                    target = locator.first
                    if not await target.is_visible():
                        continue
                    await target.scroll_into_view_if_needed(timeout=2000)
                    await target.click()
                    await page.wait_for_timeout(300)
                    await page.keyboard.type(text)
                    await page.wait_for_timeout(300)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(300)
                    return True
                except Exception:
                    continue
            return False

        for selector in AWESOME_INDY_CATEGORIES_SELECTORS:
            locator = page.locator(selector)
            try:
                if await locator.count() == 0:
                    continue
                target = locator.first
                if not await target.is_visible():
                    continue
                tag_name = await target.evaluate("(el) => el.tagName.toLowerCase()")
                if tag_name == "select":
                    options = await target.locator("option").all_inner_texts()
                    if options:
                        for item in normalized:
                            matched = next((opt for opt in options if item.lower() in (opt or "").lower()), None)
                            if matched:
                                await target.select_option(label=matched)
                                return True
                        await target.select_option(label=normalized[0])
                        return True
                if "ant-select" in (await target.get_attribute("class") or ""):
                    picked_any = False
                    for item in normalized:
                        picked_any = await _select_category_text(item) or picked_any
                    if picked_any:
                        return True
                else:
                    await target.click()
                    await page.keyboard.type(", ".join(normalized))
                    return True
            except Exception:
                continue

        for item in normalized:
            if await _select_category_text(item):
                return True

        return False

    async def fill_form(self, page, browser_helper: BrowserAutomationHelper | None, data: Dict[str, str]) -> None:
        product_name = data.get("product_name", "")
        website_url = data.get("url", "")
        tagline = data.get("tagline", "")
        categories = data.get("categories", "")
        description = data.get("description", "")
        social_links = data.get("social_links", "")
        youtube_video_url = data.get("youtube_video_url", "")

        if product_name and not (
            await self._fill_exact_name(page, "product_name", product_name)
            or await self._fill_exact_name(page, "productName", product_name)
            or await self._fill_by_label(page, [r"Product name", r"Product Name", r"Name"], product_name)
            or await self._fill_by_placeholder(page, [r"Product name", r"Name"], product_name)
            or await self._fill_first_visible_match(page, AWESOME_INDY_PRODUCT_NAME_SELECTORS, product_name)
        ):
            raise ValueError("Không tìm thấy field Product name của Awesome Indie.")

        if website_url and not (
            await self._fill_exact_name(page, "url", website_url)
            or await self._fill_exact_name(page, "website_url", website_url)
            or await self._fill_exact_name(page, "websiteUrl", website_url)
            or await self._fill_by_label(page, [r"URL", r"Website URL", r"Website"], website_url)
            or await self._fill_by_placeholder(page, [r"URL", r"Website URL", r"Website"], website_url)
            or await self._fill_first_visible_match(page, AWESOME_INDY_URL_SELECTORS, website_url)
        ):
            raise ValueError("Không tìm thấy field URL của Awesome Indie.")

        if tagline and not (
            await self._fill_exact_name(page, "tagline", tagline)
            or await self._fill_by_label(page, [r"Tagline"], tagline)
            or await self._fill_by_placeholder(page, [r"Tagline"], tagline)
            or await self._fill_first_visible_match(page, AWESOME_INDY_TAGLINE_SELECTORS, tagline)
        ):
            raise ValueError("Không tìm thấy field Tagline của Awesome Indie.")

        if categories and not (
            await self._fill_exact_name(page, "categories", categories)
            or await self._fill_exact_name(page, "category", categories)
            or await self._fill_by_label(page, [r"Categories", r"Category"], categories)
            or await self._fill_by_placeholder(page, [r"Categories", r"Category"], categories)
            or await self._fill_categories(page, categories)
            or await self._fill_first_visible_match(page, AWESOME_INDY_CATEGORIES_SELECTORS, categories)
        ):
            raise ValueError("Không tìm thấy field Categories của Awesome Indie.")

        if description and not (
            await self._fill_exact_name(page, "description", description)
            or await self._fill_exact_name(page, "productDescription", description)
            or await self._fill_by_label(page, [r"Description"], description)
            or await self._fill_by_placeholder(page, [r"Description"], description)
            or await self._fill_contenteditable(page, description)
            or await self._fill_first_visible_match(page, AWESOME_INDY_DESCRIPTION_SELECTORS, description)
        ):
            raise ValueError("Không tìm thấy field Description của Awesome Indie.")

        if social_links and not (
            await self._fill_exact_name(page, "socialLinks", social_links)
            or await self._fill_by_label(page, [r"Social links", r"Social Links"], social_links)
            or await self._fill_by_placeholder(page, [r"Social links", r"Social Links"], social_links)
            or await self._fill_social_links(page, social_links)
        ):
            raise ValueError("Không tìm thấy field Social links của Awesome Indie.")

        if youtube_video_url:
            await self._fill_exact_name(page, "youtubeVideoUrl", youtube_video_url) or \
                await self._fill_exact_name(page, "youtube_video_url", youtube_video_url) or \
                await self._fill_by_label(page, [r"YouTube video URL", r"YouTube"], youtube_video_url) or \
                await self._fill_by_placeholder(page, [r"YouTube video URL", r"YouTube"], youtube_video_url) or \
                await self._fill_first_visible_match(page, AWESOME_INDY_YOUTUBE_SELECTORS, youtube_video_url)

    async def click_add_product(self, page, browser_helper: BrowserAutomationHelper) -> bool:
        return await browser_helper.click_first_visible(page, AWESOME_INDY_ADD_PRODUCT_SELECTORS)

    async def click_submit(self, page, browser_helper: BrowserAutomationHelper) -> bool:
        return await browser_helper.click_first_visible(page, AWESOME_INDY_SUBMIT_BUTTON_SELECTORS)
