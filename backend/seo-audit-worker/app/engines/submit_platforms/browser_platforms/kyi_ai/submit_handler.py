from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict

from playwright.async_api import async_playwright

from app.auth.strategies.kyi_ai import KYIAiAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper

from .constants import KYI_AI_POPUP_SELECTORS, KYI_AI_SUCCESS_PATTERNS, KYI_AI_SUBMIT_URL
from .form_mapper import KYIAiFormMapper
from .result_parser import KYIAiResultParser


class KYIAiSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = KYIAiAuthStrategy

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = KYIAiFormMapper(self)
        self.result_parser = KYIAiResultParser()

    def _debug_enabled(self, metadata: Dict[str, Any] | None = None) -> bool:
        metadata_value = ""
        if metadata:
            metadata_value = str(metadata.get("KyiAiDebugHeadful") or metadata.get("debugHeadful") or "").strip().lower()
        if metadata_value in {"1", "true", "yes", "on"}:
            return True
        return (os.getenv("KYI_AI_DEBUG_HEADFUL", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _debug_slow_mo_ms(self) -> int:
        raw_value = (os.getenv("KYI_AI_DEBUG_SLOWMO_MS", "") or "").strip()
        if not raw_value:
            return 0
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _chrome_executable_path(self) -> str | None:
        raw_value = (os.getenv("KYI_AI_CHROME_EXECUTABLE_PATH", "") or "").strip()
        if raw_value and Path(raw_value).expanduser().exists():
            return raw_value
        return None

    async def _wait_for_success_popup(self, page, timeout_ms: int = 15000, success_event: asyncio.Event | None = None) -> bool:
        deadline = time.time() + (timeout_ms / 1000.0)

        try:
            await page.wait_for_function(
                """() => {
                    const selectors = [
                        "[data-sonner-toast][data-type='success']",
                        "[role='status'][data-type='success']",
                        "li[data-sonner-toast][data-type='success']",
                        "[data-sonner-toast]"
                    ];

                    return selectors.some((selector) => {
                        const el = document.querySelector(selector);
                        if (!el) return false;

                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        const visible = style.display !== 'none'
                            && style.visibility !== 'hidden'
                            && rect.width > 0
                            && rect.height > 0;

                        if (!visible) return false;

                        const text = (el.innerText || el.textContent || '').toLowerCase();
                        const dataType = (el.getAttribute('data-type') || '').toLowerCase();
                        return dataType === 'success' || text.includes('success') || text.includes('submitted');
                    });
                }""",
                timeout=2000,
            )
            return True
        except Exception:
            pass

        while time.time() < deadline:
            if success_event is not None and success_event.is_set():
                return True

            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
            except Exception:
                body_text = ""

            if any(pattern in body_text for pattern in KYI_AI_SUCCESS_PATTERNS):
                return True

            for selector in KYI_AI_POPUP_SELECTORS:
                try:
                    locator = page.locator(selector)
                    if await locator.count() == 0:
                        continue
                    target = locator.first
                    if await target.is_visible():
                        if selector in {"[data-sonner-toast][data-type='success']", "[role='status'][data-type='success']", "li[data-sonner-toast][data-type='success']"}:
                            return True
                        popup_text = (await target.inner_text(timeout=2000)).strip().lower()
                        if any(pattern in popup_text for pattern in KYI_AI_SUCCESS_PATTERNS):
                            return True
                except Exception:
                    continue

            await page.wait_for_timeout(500)

        return False

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        debug_enabled = self._debug_enabled(metadata)

        await self.log_audit("BrowserLaunch", "Running", "Đang khởi chạy Chrome để làm việc với Kyi AI...")

        async with async_playwright() as p:
            launch_kwargs = {
                "headless": not debug_enabled,
                "slow_mo": self._debug_slow_mo_ms() or (250 if debug_enabled else None),
                "args": ["--disable-blink-features=AutomationControlled"],
            }
            chrome_path = self._chrome_executable_path()
            if chrome_path:
                launch_kwargs["executable_path"] = chrome_path
            else:
                launch_kwargs["channel"] = "chrome"

            browser = await p.chromium.launch(**launch_kwargs)
            browser_helper = BrowserAutomationHelper(browser)
            context = None

            try:
                context = await self.create_authenticated_context(browser)
                page = await context.new_page()
                success_event = asyncio.Event()

                def _handle_dialog(dialog) -> None:
                    dialog_text = (dialog.message or "").strip().lower()
                    if any(pattern in dialog_text for pattern in KYI_AI_SUCCESS_PATTERNS):
                        success_event.set()
                    asyncio.create_task(dialog.dismiss())

                page.on("dialog", _handle_dialog)

                await self.log_audit("NavigateSubmit", "Running", f"Đang điều hướng đến: {KYI_AI_SUBMIT_URL}")
                try:
                    await page.goto(KYI_AI_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(KYI_AI_SUBMIT_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1200)

                defaults = self.form_mapper.build_defaults(metadata, url)
                await self.log_audit("FormPreview", "Success", self.result_parser.format_preview(defaults))

                if mode.lower() == "preview":
                    return {
                        "success": True,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_preview_payload(defaults),
                        "error_message": None,
                    }

                await self.log_audit("FillForm", "Running", "Đang điền form Kyi AI...")
                await self.form_mapper.fill_form(page, browser_helper, defaults)
                await page.wait_for_timeout(500)

                submit_clicked = await self.form_mapper.click_submit(page, browser_helper)
                if not submit_clicked:
                    raise ValueError("Không tìm thấy nút Submit trên Kyi AI.")

                await self.log_audit("Submit", "Running", "Đã bấm Submit. Đang chờ pop up success của Kyi AI...")

                if not await self._wait_for_success_popup(page, timeout_ms=15000, success_event=success_event):
                    err_msg = "Đã bấm Submit nhưng chưa thấy pop up success rõ ràng từ Kyi AI."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit("Submit", "Success", f"Kyi AI đã hoàn tất submit. Thời gian: {duration}ms", duration)

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(defaults, final_url=page.url),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác Kyi AI: {str(e)}"
                await self.log_audit("Submit", "Failed", err_msg, duration)
                return {
                    "success": False,
                    "response_data": None,
                    "error_message": err_msg,
                }
            finally:
                if context is not None:
                    await context.close()
                await browser.close()
