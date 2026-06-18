from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict

from playwright.async_api import async_playwright

from app.auth.strategies.awesome_indie import AwesomeIndieAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper

from .constants import (
    AWESOME_INDY_CATEGORIES_URL,
    AWESOME_INDY_HOME_URL,
    AWESOME_INDY_MY_PRODUCTS_URL,
    AWESOME_INDY_POST_PRODUCT_URL,
    AWESOME_INDY_SUCCESS_PATTERNS,
    AWESOME_INDY_SUCCESS_SELECTORS,
    AWESOME_INDY_SUBMIT_URL,
)
from .form_mapper import AwesomeIndieFormMapper
from .result_parser import AwesomeIndieResultParser


class AwesomeIndieSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = AwesomeIndieAuthStrategy

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = AwesomeIndieFormMapper(self)
        self.result_parser = AwesomeIndieResultParser()

    def _debug_enabled(self, metadata: Dict[str, Any] | None = None) -> bool:
        metadata_value = ""
        if metadata:
            metadata_value = str(metadata.get("AwesomeIndieDebugHeadful") or metadata.get("debugHeadful") or "").strip().lower()
        if metadata_value in {"1", "true", "yes", "on"}:
            return True
        return (os.getenv("AWESOME_INDIE_DEBUG_HEADFUL", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _debug_slow_mo_ms(self) -> int:
        raw_value = (os.getenv("AWESOME_INDIE_DEBUG_SLOWMO_MS", "") or "").strip()
        if not raw_value:
            return 0
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _chrome_executable_path(self) -> str | None:
        raw_value = (os.getenv("AWESOME_INDIE_CHROME_EXECUTABLE_PATH", "") or "").strip()
        if raw_value and Path(raw_value).expanduser().exists():
            return raw_value
        return None

    async def _looks_like_auth_screen(self, page) -> bool:
        current_url = (page.url or "").lower()
        if any(fragment in current_url for fragment in ("accounts.google", "/login", "/signin", "/sign-in", "/auth")):
            return True

        try:
            body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
        except Exception:
            body_text = ""

        auth_patterns = (
            "sign in with google",
            "continue with google",
            "sign in",
            "log in",
            "login",
        )
        return any(pattern in body_text for pattern in auth_patterns)

    async def _wait_for_success(self, page, timeout_ms: int = 15000, success_event: asyncio.Event | None = None) -> bool:
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
                        return dataType === 'success' || text.includes('success') || text.includes('created') || text.includes('added');
                    });
                }""",
                timeout=2500,
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

            if any(pattern in body_text for pattern in AWESOME_INDY_SUCCESS_PATTERNS):
                return True

            for selector in AWESOME_INDY_SUCCESS_SELECTORS:
                try:
                    locator = page.locator(selector)
                    if await locator.count() == 0:
                        continue
                    target = locator.first
                    if await target.is_visible():
                        popup_text = (await target.inner_text(timeout=2000)).strip().lower()
                        if any(pattern in popup_text for pattern in AWESOME_INDY_SUCCESS_PATTERNS):
                            return True
                except Exception:
                    continue

            await page.wait_for_timeout(500)

        return False

    async def _wait_for_post_response(self, page, timeout_ms: int = 20000) -> bool:
        try:
            response = await page.wait_for_response(
                lambda resp: AWESOME_INDY_POST_PRODUCT_URL in resp.url
                and resp.request.method.upper() == "POST"
                and resp.status < 400,
                timeout=timeout_ms,
            )
            return response is not None
        except Exception:
            return False

    async def _read_categories(self, page) -> list[str]:
        try:
            result = await page.evaluate(
                """async (categoriesUrl) => {
                    try {
                        const response = await fetch(categoriesUrl, { credentials: 'include' });
                        const data = await response.json();
                        return Array.isArray(data) ? data : (data?.data || data?.categories || []);
                    } catch (error) {
                        return [];
                    }
                }""",
                AWESOME_INDY_CATEGORIES_URL,
            )
            if isinstance(result, list):
                normalized = []
                for item in result:
                    if isinstance(item, str) and item.strip():
                        normalized.append(item.strip())
                        continue
                    if isinstance(item, dict):
                        for key in ("name", "title", "label", "value"):
                            raw_value = item.get(key)
                            if isinstance(raw_value, str) and raw_value.strip():
                                normalized.append(raw_value.strip())
                                break
                return normalized
        except Exception:
            pass
        return []

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        debug_enabled = self._debug_enabled(metadata)

        await self.log_audit("BrowserLaunch", "Running", "Đang khởi chạy Chrome để làm việc với Awesome Indie...")

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
                    if any(pattern in dialog_text for pattern in AWESOME_INDY_SUCCESS_PATTERNS):
                        success_event.set()
                    asyncio.create_task(dialog.dismiss())

                page.on("dialog", _handle_dialog)

                await self.log_audit("NavigateHome", "Running", f"Đang điều hướng đến: {AWESOME_INDY_HOME_URL}")
                try:
                    await page.goto(AWESOME_INDY_HOME_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(AWESOME_INDY_HOME_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1200)

                if await self._looks_like_auth_screen(page):
                    err_msg = "Awesome Indie đang yêu cầu Google OAuth. Hãy connect account lại rồi chạy submit."
                    await self.log_audit("NavigateHome", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                if not await self.form_mapper.click_add_product(page, browser_helper):
                    await self.log_audit("NavigateSubmit", "Running", "Không thấy nút AddProduct ở home, thử đi thẳng sang trang submit...")
                    try:
                        await page.goto(AWESOME_INDY_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        await page.goto(AWESOME_INDY_SUBMIT_URL, wait_until="load", timeout=30000)
                else:
                    await page.wait_for_timeout(1200)

                if await self._looks_like_auth_screen(page):
                    err_msg = "Awesome Indie vẫn đang ở màn hình Google OAuth. Hãy hoàn tất đăng nhập rồi chạy lại."
                    await self.log_audit("NavigateSubmit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                if "/submit" not in (page.url or ""):
                    try:
                        await page.goto(AWESOME_INDY_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        await page.goto(AWESOME_INDY_SUBMIT_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1200)

                defaults = self.form_mapper.build_defaults(metadata, url)
                if not defaults.get("categories"):
                    categories = await self._read_categories(page)
                    if categories:
                        defaults["categories"] = categories[0]

                await self.log_audit("FormPreview", "Success", self.result_parser.format_preview(defaults))

                if mode.lower() == "preview":
                    return {
                        "success": True,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_preview_payload(defaults),
                        "error_message": None,
                    }

                await self.log_audit("FillForm", "Running", "Đang điền form Awesome Indie...")
                await self.form_mapper.fill_form(page, browser_helper, defaults)
                await page.wait_for_timeout(500)

                post_response_task = asyncio.create_task(self._wait_for_post_response(page, timeout_ms=20000))
                if not await self.form_mapper.click_submit(page, browser_helper):
                    raise ValueError("Không tìm thấy nút Submit trên Awesome Indie.")

                await self.log_audit("Submit", "Running", "Đã bấm Submit. Đang chờ Awesome Indie phản hồi thành công...")

                post_response_seen = await post_response_task
                popup_seen = await self._wait_for_success(page, timeout_ms=15000, success_event=success_event)

                if not post_response_seen and not popup_seen and not success_event.is_set():
                    await self.log_audit("Submit", "Running", f"Không bắt được response POST. Sẽ kiểm tra tiếp trang {AWESOME_INDY_MY_PRODUCTS_URL}.")
                    try:
                        await page.goto(AWESOME_INDY_MY_PRODUCTS_URL, wait_until="domcontentloaded", timeout=15000)
                    except Exception:
                        pass
                    popup_seen = await self._wait_for_success(page, timeout_ms=8000, success_event=success_event)

                if not post_response_seen and not popup_seen and not success_event.is_set():
                    err_msg = "Đã bấm Submit nhưng chưa thấy phản hồi success rõ ràng từ Awesome Indie."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit("Submit", "Success", f"Awesome Indie đã hoàn tất submit. Thời gian: {duration}ms", duration)

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(defaults, final_url=page.url),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác Awesome Indie: {str(e)}"
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
