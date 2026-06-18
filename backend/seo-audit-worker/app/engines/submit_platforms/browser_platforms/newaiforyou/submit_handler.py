from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict

from playwright.async_api import async_playwright

from app.auth.strategies.newaiforyou import NewAIForYouAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper

from .constants import (
    NEWAIFORYOU_BASE_URL,
    NEWAIFORYOU_HOME_URL,
    NEWAIFORYOU_MODAL_SELECTORS,
    NEWAIFORYOU_POST_PRODUCT_URL,
    NEWAIFORYOU_SUCCESS_PATTERNS,
    NEWAIFORYOU_SUCCESS_SELECTORS,
    NEWAIFORYOU_SUBMIT_URL,
)
from .form_mapper import NewAIForYouFormMapper
from .result_parser import NewAIForYouResultParser


class NewAIForYouSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = NewAIForYouAuthStrategy

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = NewAIForYouFormMapper(self)
        self.result_parser = NewAIForYouResultParser()

    def _debug_enabled(self, metadata: Dict[str, Any] | None = None) -> bool:
        metadata_value = ""
        if metadata:
            metadata_value = str(metadata.get("NewAIForYouDebugHeadful") or metadata.get("debugHeadful") or "").strip().lower()
        if metadata_value in {"1", "true", "yes", "on"}:
            return True
        return (os.getenv("NEWAIFORYOU_DEBUG_HEADFUL", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _debug_slow_mo_ms(self) -> int:
        raw_value = (os.getenv("NEWAIFORYOU_DEBUG_SLOWMO_MS", "") or "").strip()
        if not raw_value:
            return 0
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _chrome_executable_path(self) -> str | None:
        raw_value = (os.getenv("NEWAIFORYOU_CHROME_EXECUTABLE_PATH", "") or "").strip()
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

        # The live site shows a generic "Log In" label in the navbar on both
        # home and submit pages, so we only treat it as an auth screen when the
        # page clearly mentions Google OAuth.
        google_auth_patterns = (
            "continue with google",
            "sign in with google",
            "choose an account",
            "use your google account",
            "google oauth",
        )
        return any(pattern in body_text for pattern in google_auth_patterns)

    async def _wait_for_success_modal(self, page, timeout_ms: int = 15000, success_event: asyncio.Event | None = None) -> bool:
        deadline = time.time() + (timeout_ms / 1000.0)

        while time.time() < deadline:
            if success_event is not None and success_event.is_set():
                return True

            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
            except Exception:
                body_text = ""

            if any(pattern in body_text for pattern in NEWAIFORYOU_SUCCESS_PATTERNS):
                return True

            for selector in NEWAIFORYOU_MODAL_SELECTORS + NEWAIFORYOU_SUCCESS_SELECTORS:
                try:
                    locator = page.locator(selector)
                    if await locator.count() == 0:
                        continue
                    target = locator.first
                    if not await target.is_visible():
                        continue
                    text = (await target.inner_text(timeout=2000)).strip().lower()
                    if any(pattern in text for pattern in NEWAIFORYOU_SUCCESS_PATTERNS):
                        return True
                except Exception:
                    continue

            if (page.url or "").rstrip("/") == NEWAIFORYOU_HOME_URL.rstrip("/"):
                return True

            await page.wait_for_timeout(500)

        return False

    async def _wait_for_home_redirect(self, page, timeout_ms: int = 12000) -> bool:
        deadline = time.time() + (timeout_ms / 1000.0)
        while time.time() < deadline:
            if (page.url or "").rstrip("/") == NEWAIFORYOU_HOME_URL.rstrip("/"):
                return True
            await page.wait_for_timeout(500)
        return False

    async def _wait_for_post_response(self, page, timeout_ms: int = 20000) -> bool:
        try:
            response = await page.wait_for_response(
                lambda resp: NEWAIFORYOU_POST_PRODUCT_URL in resp.url
                and resp.request.method.upper() == "POST"
                and resp.status < 400,
                timeout=timeout_ms,
            )
            return response is not None
        except Exception:
            return False

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        debug_enabled = self._debug_enabled(metadata)

        await self.log_audit("BrowserLaunch", "Running", "Đang khởi chạy Chrome để làm việc với New AI For You...")

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
                    if any(pattern in dialog_text for pattern in NEWAIFORYOU_SUCCESS_PATTERNS):
                        success_event.set()
                    asyncio.create_task(dialog.dismiss())

                page.on("dialog", _handle_dialog)

                await self.log_audit("NavigateHome", "Running", f"Đang điều hướng đến: {NEWAIFORYOU_HOME_URL}")
                try:
                    await page.goto(NEWAIFORYOU_HOME_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(NEWAIFORYOU_HOME_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1200)

                if await self._looks_like_auth_screen(page):
                    err_msg = "New AI For You đang yêu cầu Google OAuth. Hãy connect account lại rồi chạy submit."
                    await self.log_audit("NavigateHome", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                if not await self.form_mapper.click_add_product(page, browser_helper):
                    await self.log_audit("NavigateSubmit", "Running", "Không thấy nút AddProduct ở home, thử đi thẳng sang trang submit...")
                    try:
                        await page.goto(NEWAIFORYOU_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        await page.goto(NEWAIFORYOU_SUBMIT_URL, wait_until="load", timeout=30000)
                else:
                    await page.wait_for_timeout(1200)

                if await self._looks_like_auth_screen(page):
                    err_msg = "New AI For You vẫn đang ở màn hình Google OAuth. Hãy hoàn tất đăng nhập rồi chạy lại."
                    await self.log_audit("NavigateSubmit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                if "/submit" not in (page.url or ""):
                    try:
                        await page.goto(NEWAIFORYOU_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        await page.goto(NEWAIFORYOU_SUBMIT_URL, wait_until="load", timeout=30000)

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

                await self.log_audit("FillForm", "Running", "Đang điền form New AI For You...")
                await self.form_mapper.fill_form(page, browser_helper, defaults)
                await page.wait_for_timeout(500)

                post_response_task = asyncio.create_task(self._wait_for_post_response(page, timeout_ms=20000))
                if not await self.form_mapper.click_submit(page, browser_helper):
                    raise ValueError("Không tìm thấy nút Submit trên New AI For You.")

                await self.log_audit("Submit", "Running", "Đã bấm Submit. Đang chờ modal success và redirect về home...")

                post_response_seen = await post_response_task
                modal_seen = await self._wait_for_success_modal(page, timeout_ms=15000, success_event=success_event)
                home_seen = await self._wait_for_home_redirect(page, timeout_ms=15000)

                if not post_response_seen and not modal_seen and not home_seen and not success_event.is_set():
                    err_msg = "Đã bấm Submit nhưng chưa thấy modal success hoặc redirect home từ New AI For You."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit("Submit", "Success", f"New AI For You đã hoàn tất submit. Thời gian: {duration}ms", duration)

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(defaults, final_url=page.url),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác New AI For You: {str(e)}"
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
