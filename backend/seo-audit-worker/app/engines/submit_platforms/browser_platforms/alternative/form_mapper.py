from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from app.platforms.browser_automation import BrowserAutomationHelper

from .constants import ALTERNATIVE_MONETIZATION_OPTIONS, ALTERNATIVE_STATUS_OPTIONS, ALTERNATIVE_TYPE_OPTIONS


class AlternativeFormMapper:
    def __init__(self, handler: Any):
        self.handler = handler

    def _debug_enabled(self) -> bool:
        return bool(getattr(self.handler, "_debug_enabled", lambda: False)())

    def _debug_print(self, title: str, payload: Any) -> None:
        if not self._debug_enabled():
            return
        print(f"\n[AlternativeFormMapperDebug] {title}:")
        if isinstance(payload, (dict, list)):
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(payload)

    def build_defaults(self, metadata: Dict[str, Any], url: str) -> Dict[str, str]:
        return {
            "software_name": metadata.get("SiteName") or metadata.get("SoftwareName") or "My Software",
            "icon_path": metadata.get("IconPath") or metadata.get("IconFilePath") or metadata.get("IconLocalPath") or metadata.get("LogoPath") or "",
            "category": metadata.get("Category") or metadata.get("Categories") or "",
            "short_description": metadata.get("ShortDescription") or metadata.get("Description") or "",
            "full_description": metadata.get("FullDescription") or metadata.get("ProductDescription") or metadata.get("Description") or "",
            "homepage_url": metadata.get("HomepageUrl") or url,
            "pricing_url": metadata.get("PricingUrl") or "",
            "type": metadata.get("Type") or metadata.get("ProductType") or "online",
            "monetization": metadata.get("Monetization") or metadata.get("Pricing") or "free",
            "status": metadata.get("Status") or "live",
            "platforms": metadata.get("Platforms") or "",
            "features": metadata.get("Features") or metadata.get("Keywords") or "",
            "social_links": metadata.get("SocialLinks") or "https://example.com",
            "social_link_type": metadata.get("AlternativeSocialLinkType") or "twitter",
            "pricing_name": metadata.get("AlternativePricingName") or "",
            "pricing_cost": metadata.get("AlternativePricingCost") or "29",
            "synonyms": metadata.get("Synonyms") or "",
        }

    async def _fill_select_by_label(self, page, label: str, value: str) -> bool:
        if not value:
            return False
        try:
            select = page.get_by_label(re.compile(label, re.IGNORECASE))
            if await select.count() > 0:
                try:
                    await select.first.select_option(value=value)
                except Exception:
                    await select.first.select_option(label=value)
                return True
        except Exception:
            pass
        return False

    async def _fill_select_by_selectors(self, page, selectors, value: str) -> bool:
        if not value:
            return False
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue

            target = locator.first
            try:
                if await target.is_visible():
                    try:
                        await target.select_option(value=value)
                    except Exception:
                        await target.select_option(label=value)
                    return True
            except Exception:
                continue
        return False

    async def _read_first_visible_value(self, page, selectors) -> str:
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue

            target = locator.first
            try:
                if not await target.is_visible():
                    continue
                tag_name = await target.evaluate("(el) => el.tagName.toLowerCase()")
                if tag_name in {"input", "textarea", "select"}:
                    return (await target.input_value()).strip()
                return (await target.text_content() or "").strip()
            except Exception:
                continue
        return ""

    async def _wait_for_any_visible(self, page, selectors, timeout_ms: int = 15000) -> bool:
        try:
            await page.wait_for_function(
                """(selectors) => {
                    return selectors.some((selector) => {
                        const el = document.querySelector(selector);
                        if (!el) return false;
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
                    });
                }""",
                arg=selectors,
                timeout=timeout_ms,
            )
            return True
        except Exception:
            return False

    async def _wait_for_loading_overlay_clear(self, page, timeout_ms: int = 10000) -> None:
        try:
            overlay = page.locator("div.loading-background")
            if await overlay.count() == 0:
                return
            await overlay.first.wait_for(state="hidden", timeout=timeout_ms)
        except Exception:
            try:
                await page.wait_for_function(
                    """() => {
                        const el = document.querySelector('div.loading-background');
                        if (!el) return true;
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        return style.display === 'none' || style.visibility === 'hidden' || rect.width === 0 || rect.height === 0;
                    }""",
                    timeout=timeout_ms,
                )
            except Exception:
                return

    async def _fill_input_and_press_enter(self, page, selectors, value: str) -> bool:
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
                    await target.press("Enter")
                    return True
            except Exception:
                continue
        return False

    async def _require_filled_input(self, page, browser_helper: BrowserAutomationHelper, selectors, value: str, field_name: str) -> None:
        if not value:
            raise ValueError(f"Thiếu giá trị bắt buộc cho field: {field_name}.")
        filled = await browser_helper.fill_first_visible(page, selectors, value)
        if not filled:
            raise ValueError(f"Không tìm thấy field bắt buộc: {field_name}.")

        observed = await self._read_first_visible_value(page, selectors)
        if observed and observed != value:
            raise ValueError(f"Field {field_name} không nhận đúng dữ liệu (expected='{value}', actual='{observed}').")

    async def _require_select_option(self, page, label: str, value: str) -> None:
        if not value:
            raise ValueError(f"Thiếu giá trị bắt buộc cho field: {label}.")
        filled = await self._fill_select_by_label(page, label, value)
        if not filled:
            raise ValueError(f"Không tìm thấy select bắt buộc: {label}.")

        observed = ""
        try:
            select = page.get_by_label(re.compile(label, re.IGNORECASE))
            if await select.count() > 0:
                observed = (await select.first.input_value()).strip()
        except Exception:
            observed = ""
        if observed and observed != value:
            raise ValueError(f"Select {label} không nhận đúng option (expected='{value}', actual='{observed}').")

    async def _require_select_option_by_selectors(self, page, selectors, value: str, field_name: str) -> None:
        if not value:
            raise ValueError(f"Thiếu giá trị bắt buộc cho field: {field_name}.")
        filled = await self._fill_select_by_selectors(page, selectors, value)
        if not filled:
            raise ValueError(f"Không tìm thấy select bắt buộc: {field_name}.")

        observed = ""
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue
            target = locator.first
            try:
                if await target.is_visible():
                    observed = (await target.input_value()).strip()
                    if observed:
                        break
            except Exception:
                continue

        if observed and observed != value:
            raise ValueError(f"Select {field_name} không nhận đúng option (expected='{value}', actual='{observed}').")

    async def _fill_textarea_by_label(self, page, label: str, value: str) -> bool:
        if not value:
            return False
        try:
            textarea = page.get_by_label(re.compile(label, re.IGNORECASE))
            if await textarea.count() > 0:
                await textarea.first.fill(value)
                return True
        except Exception:
            pass
        return False

    async def _require_textarea(self, page, browser_helper: BrowserAutomationHelper, selectors, value: str, field_name: str) -> None:
        if not value:
            raise ValueError(f"Thiếu giá trị bắt buộc cho field: {field_name}.")

        filled = await browser_helper.fill_first_visible(page, selectors, value)
        if not filled:
            raise ValueError(f"Không tìm thấy textarea bắt buộc: {field_name}.")

        observed = await self._read_first_visible_value(page, selectors)
        if observed and observed != value:
            raise ValueError(
                f"Textarea {field_name} không nhận đúng dữ liệu (expected='{value}', actual='{observed}')."
            )

    async def _require_icon_upload(self, page, icon_path: str) -> None:
        if not icon_path:
            raise ValueError("Thiếu icon bắt buộc. Hãy truyền --icon-path với file ảnh local.")

        resolved_icon_path = Path(icon_path).expanduser()
        if not resolved_icon_path.exists():
            raise ValueError(f"Icon path không tồn tại: {resolved_icon_path}")

        input_locator = page.locator(
            ".field.file input[type='file'], "
            "input[type='file'][accept*='image'], "
            "input[type='file']"
        )

        if await input_locator.count() == 0:
            raise ValueError("Không tìm thấy input upload Icon trên Alternative.")

        target = input_locator.first

        await target.scroll_into_view_if_needed(timeout=2000)

        try:
            async with page.expect_file_chooser() as chooser_info:
                await target.click(force=True)

            chooser = await chooser_info.value
            await chooser.set_files(str(resolved_icon_path))

        except Exception:
            await target.set_input_files(str(resolved_icon_path))

        # Đợi overlay loading biến mất
        try:
            loading = page.locator(".loading-background")

            if await loading.count() > 0:
                print("[AlternativeDebug] Waiting icon upload...")

                await loading.first.wait_for(
                    state="hidden",
                    timeout=30000
                )

                print("[AlternativeDebug] Icon upload completed")

        except Exception as ex:
            print(f"[AlternativeDebug] Loading wait timeout: {ex}")

        await page.wait_for_timeout(1000)

    async def fill_initial_wizard_step(self, page, browser_helper: BrowserAutomationHelper, data: Dict[str, str]) -> None:
        opened = await browser_helper.click_first_visible(
            page,
            [
                ".block .button.is-primary",
                "span.button.is-primary",
                "button:has-text('Submit Software')",
                "text=Submit Software",
            ],
        )
        if not opened:
            raise ValueError("Không tìm thấy nút Submit Software để mở form Alternative.")

        await page.wait_for_timeout(1200)
        await browser_helper.wait_for_text_visible(page, "body", "Software Name", timeout=15000)

        software_name = data.get("software_name", "")
        await self._require_filled_input(
            page,
            browser_helper,
            [
                "input[placeholder='Software Name']",
                "input[name='softwareName']",
                "input[name='name']",
                "input[type='text']",
            ],
            software_name,
            "Software Name",
        )

        loading = page.locator(".loading-background")

        try:
            await loading.wait_for(
                state="hidden",
                timeout=15000
            )
        except:
            pass

        clicked = await browser_helper.click_first_visible(
            page,
            [
                "section.modal-card-body span.button.is-primary:has-text('Next')",
                "section.modal-card-body span.button.is-primary:has-text('Continue')",
                "span.button.is-primary:has-text('Next')",
                "span.button.is-primary:has-text('Continue')",
                "button:has-text('Next')",
                "button:has-text('Continue')",
                "button[type='submit']",
                "text=Next",
                "text=Continue",
            ],
        )
        if not clicked:
            raise ValueError("Không tìm thấy nút Next/Continue ở bước đầu của Alternative.")

        await page.wait_for_timeout(1200)

    async def fill_form(self, page, browser_helper: BrowserAutomationHelper, data: Dict[str, str]) -> None:
        await self._wait_for_any_visible(
            page,
            [
                "input[placeholder='Homepage URL']",
                "input[placeholder='Pricing URL']",
                "textarea[maxlength='300']",
                "textarea[maxlength='1000']",
            ],
            timeout_ms=15000,
        )
        await self._require_icon_upload(page, data.get("icon_path", ""))
        await self._require_filled_input(
            page,
            browser_helper,
            [
                "input[placeholder='Homepage URL']",
                "section.modal-card-body input[placeholder='Homepage URL']",
                "label:has-text('Homepage URL') + div input",
                "input[name='homepageUrl']",
                "input[name='url']",
                "input[type='url']",
            ],
            data.get("homepage_url", ""),
            "Homepage URL",
        )
        await self._require_filled_input(
            page,
            browser_helper,
            [
                "input[placeholder='Pricing URL']",
                "section.modal-card-body input[placeholder='Pricing URL']",
                "label:has-text('Pricing URL (if available)') + div input",
                "input[name='pricingUrl']",
            ],
            data.get("pricing_url", ""),
            "Pricing URL",
        )
        await self._require_textarea(
            page,
            browser_helper,
            [
                "section.modal-card-body textarea[minlength='100'][maxlength='300']",
                "textarea[minlength='100'][maxlength='300']",
                "textarea[rows='3']",
                "textarea",
            ],
            data.get("short_description", ""),
            "Short Description",
        )
        await self._require_textarea(
            page,
            browser_helper,
            [
                "section.modal-card-body textarea[minlength='200'][maxlength='1000']",
                "textarea[minlength='200'][maxlength='1000']",
                "textarea[rows='5']",
                "textarea",
            ],
            data.get("full_description", ""),
            "Full Description",
        )

        await self._require_select_option_by_selectors(
            page,
            [
                "section.modal-card-body .field:has-text('Category') select",
                "section.modal-card-body select[required='required']",
                "section.modal-card-body .field:nth-of-type(2) select",
                "select[required='required']",
            ],
            data.get("category", ""),
            "Category",
        )
        await self._require_select_option_by_selectors(
            page,
            [
                "section.modal-card-body .columns .column:nth-of-type(1) select",
                "section.modal-card-body select:has(option[value='desktop'])",
                "select:has(option[value='desktop'])",
            ],
            self._normalize_option(data.get("type", ""), ALTERNATIVE_TYPE_OPTIONS, "online"),
            "Type",
        )
        await self._require_select_option_by_selectors(
            page,
            [
                "section.modal-card-body .columns .column:nth-of-type(2) select",
                "section.modal-card-body select:has(option[value='opensource'])",
                "select:has(option[value='opensource'])",
            ],
            self._normalize_option(data.get("monetization", ""), ALTERNATIVE_MONETIZATION_OPTIONS, "free"),
            "Monetization",
        )
        await self._require_select_option_by_selectors(
            page,
            [
                "section.modal-card-body .columns .column:nth-of-type(3) select",
                "section.modal-card-body select:has(option[value='announced'])",
                "select:has(option[value='announced'])",
            ],
            self._normalize_option(data.get("status", ""), ALTERNATIVE_STATUS_OPTIONS, "live"),
            "Status",
        )

        if data.get("platforms"):
            if not await self._fill_input_and_press_enter(
                page,
                [
                    "input[placeholder*='Please select all matching platforms']",
                    "input[placeholder*='matching platforms']",
                    "input[name='platforms']",
                    "input[role='combobox']",
                ],
                data.get("platforms", ""),
            ):
                raise ValueError("Không tìm thấy field bắt buộc: Platforms.")

        if data.get("features"):
            if not await self._fill_input_and_press_enter(
                page,
                [
                    "input[placeholder*='Start typing features']",
                    "input[name='features']",
                ],
                data.get("features", ""),
            ):
                raise ValueError("Không tìm thấy field bắt buộc: Features.")

        if data.get("social_links"):
            self._debug_print(
                "SocialLinkDebugInputs",
                await page.locator("input").evaluate_all(
                    """
                    els => els.map(e => ({
                        placeholder: e.placeholder,
                        name: e.name,
                        type: e.type
                    }))
                    """
                ),
            )
            if not await self._fill_social_link(page, browser_helper, data.get("social_links", ""), data.get("social_link_type", "twitter")):
                raise ValueError("Không tìm thấy field bắt buộc: Social Links.")

        if data.get("pricing_name"):
            if not await browser_helper.fill_first_visible(page, ["input[placeholder*=\"Name (e.g. 'Premium')\"]", "input[name='pricingName']"], data.get("pricing_name", "")):
                raise ValueError("Không tìm thấy field bắt buộc: Pricing Name.")
        if data.get("pricing_cost"):
            if not await browser_helper.fill_first_visible(page, ["input[placeholder*='Cost per month (USD)']", "input[name='pricingCost']"], data.get("pricing_cost", "")):
                raise ValueError("Không tìm thấy field bắt buộc: Pricing Cost.")
            await self._click_add_pricing(page, browser_helper)

        if data.get("synonyms"):
            if not await self._fill_input_and_press_enter(
                page,
                [
                    "input[placeholder*='Add synonyms and press Enter']",
                    "input[name='synonyms']",
                ],
                data.get("synonyms", ""),
            ):
                raise ValueError("Không tìm thấy field bắt buộc: Synonyms.")

    async def _fill_social_link(self, page, browser_helper: BrowserAutomationHelper, value: str, link_type: str = "twitter") -> bool:
        if not value:
            return True
        links = [item.strip() for item in re.split(r"[,\n]+", value) if item.strip()]
        if not links:
            return False

        link_url = links[0]
        url_input = page.locator("section.modal-card-body input[placeholder='https://...']")
        if await url_input.count() == 0:
            url_input = page.locator("input[placeholder='https://...']")
        if await url_input.count() == 0:
            return False

        container = url_input.first.locator(
            "xpath=ancestor::div[contains(concat(' ', normalize-space(@class), ' '), ' field ') and contains(concat(' ', normalize-space(@class), ' '), ' is-grouped ')]"
        ).first

        try:
            if await container.count() == 0:
                return False

            input_locator = container.locator("input[placeholder='https://...']").first
            await input_locator.scroll_into_view_if_needed(timeout=2000)
            await input_locator.fill(link_url)

            select = container.locator("select").first
            await select.select_option(link_type)
            await self._wait_for_loading_overlay_clear(page, timeout_ms=15000)
            await page.wait_for_timeout(300)

            button = container.locator("button:has-text('Add Link')").first
            await button.scroll_into_view_if_needed(timeout=2000)
            try:
                await button.click(timeout=3000)
            except Exception:
                await self._wait_for_loading_overlay_clear(page, timeout_ms=3000)
                await button.click(force=True, timeout=3000)
            await page.wait_for_timeout(500)
            return True
        except Exception as ex:
            print(f"[SOCIAL_LINK_ERROR] {ex}")
            raise
            
        return False

    async def _click_add_pricing(self, page, browser_helper: BrowserAutomationHelper) -> bool:
        return await browser_helper.click_first_visible(
            page,
            [
                "button:has-text('Add Pricing')",
                "div:has-text('Pricing (if available)') button:has-text('Add Pricing')",
            ],
        )

    def _normalize_option(self, value: str, options: list[str], default: str) -> str:
        candidate = (value or "").strip()
        aliases = {
            "type": {
                "desktop client": "desktop",
                "desktop app": "desktop",
                "app": "app",
                "mobile app": "app",
                "online / saas": "online",
                "saas": "online",
                "web app": "online",
            },
            "monetization": {
                "free": "free",
                "freemium": "freemium",
                "paid": "paid",
                "open source": "opensource",
            },
            "status": {
                "announced": "announced",
                "released": "live",
                "live": "live",
                "abandoned": "abandoned",
                "discontinued": "offline",
                "offline": "offline",
            },
        }

        normalized = candidate.lower()
        for alias_map in aliases.values():
            if normalized in alias_map:
                return alias_map[normalized]

        for option in options:
            if candidate.lower() == option.lower():
                return option
        return default
