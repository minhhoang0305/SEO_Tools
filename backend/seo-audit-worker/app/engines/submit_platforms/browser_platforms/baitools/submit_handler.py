from __future__ import annotations

import json
import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict

from playwright.async_api import async_playwright

from app.auth.strategies.baitools import BAItoolsAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.retry_timeout import RetryTimeoutHandler

from .constants import BAITOOLS_FINISH_PATTERNS, BAITOOLS_SUBMIT_URL
from .form_mapper import BAItoolsFormMapper
from .result_parser import BAItoolsResultParser


class BAItoolsSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = BAItoolsAuthStrategy
    OAUTH_PATTERNS = (
        "accounts.google",
        "oauth",
        "sign in",
        "sign in with google",
        "choose an account",
        "login",
        "authorize",
    )

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = BAItoolsFormMapper(self)
        self.result_parser = BAItoolsResultParser()

    def _debug_enabled(self) -> bool:
        return (os.getenv("BAITOOLS_DEBUG_HEADFUL", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _debug_slow_mo_ms(self) -> int:
        raw_value = (os.getenv("BAITOOLS_DEBUG_SLOWMO_MS", "") or "").strip()
        if not raw_value:
            return 0
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _browser_channel(self) -> str:
        raw_value = (os.getenv("BAITOOLS_BROWSER_CHANNEL", "") or "").strip()
        return raw_value or "chrome"

    def _chrome_executable_path(self) -> str | None:
        raw_value = (os.getenv("BAITOOLS_CHROME_EXECUTABLE_PATH", "") or "").strip()
        if raw_value and Path(raw_value).expanduser().exists():
            return raw_value
        return None

    def _wait_for_manual_oauth_enabled(self) -> bool:
        return (os.getenv("BAITOOLS_WAIT_FOR_MANUAL_OAUTH", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    async def _detect_oauth_screen(self, page) -> bool:
        current_url = (page.url or "").lower()
        if any(pattern in current_url for pattern in ("accounts.google", "oauth", "login", "signin")):
            return True

        try:
            body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
        except Exception:
            body_text = ""
        if not body_text:
            return False
        return any(pattern in body_text for pattern in self.OAUTH_PATTERNS)

    async def _pause_for_manual_oauth(self, page, stage: str) -> bool:
        if not await self._detect_oauth_screen(page):
            return False

        message = (
            f"BAI.tools đang yêu cầu OAuth ở bước {stage}. "
            "Hãy hoàn tất đăng nhập trong Chrome rồi nhấn Enter để tiếp tục..."
        )
        await self.log_audit("ManualAction", "Running", message)

        if self._debug_enabled():
            await page.screenshot(
                path=str(Path(__file__).resolve().parents[5] / ".playwright" / f"baitools-oauth-{stage}.png"),
                full_page=True,
            )

        if not self._wait_for_manual_oauth_enabled():
            return True

        await asyncio.to_thread(input, f"{message}\n")
        await page.wait_for_timeout(1000)
        return await self._detect_oauth_screen(page)

    async def _wait_for_finish_state(self, page, timeout_ms: int = 15000) -> tuple[str, str]:
        deadline = time.time() + (timeout_ms / 1000.0)
        while time.time() < deadline:
            current_url = page.url or ""
            if any(fragment in current_url.lower() for fragment in ("/finish", "thank-you", "success")):
                return current_url, ""

            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip()
            except Exception:
                body_text = ""

            lower_body = body_text.lower()
            if any(pattern in lower_body for pattern in BAITOOLS_FINISH_PATTERNS):
                return current_url, body_text

            await page.wait_for_timeout(500)

        return page.url or "", ""

    def _api_enabled(self, metadata: Dict[str, Any]) -> bool:
        raw_value = metadata.get("BAIToolsUseApi") or metadata.get("useApi") or os.getenv("BAITOOLS_USE_API", "")
        return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}

    async def _submit_via_api(self, page, defaults: Dict[str, str]) -> Dict[str, Any]:
        payload = {
            "toolName": defaults.get("tool_name", ""),
            "toolUrl": defaults.get("website_url", ""),
            "planIndex": int(defaults.get("plan_index") or 0),
            "locale": defaults.get("locale", "en"),
        }

        await self.log_audit(
            "ApiSubmit",
            "Running",
            f"Đang gửi API submit tới BAI.tools: /api/tools/submit. Payload: {payload}",
        )

        try:
            result = await page.evaluate(
                """async (payload) => {
                    const response = await fetch('/api/tools/submit', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': '*/*'
                        },
                        credentials: 'include',
                        body: JSON.stringify(payload)
                    });

                    let data = null;
                    try {
                        data = await response.json();
                    } catch (err) {
                        try {
                            data = await response.text();
                        } catch (textErr) {
                            data = null;
                        }
                    }

                    return {
                        status: response.status,
                        ok: response.ok,
                        data,
                    };
                }""",
                payload,
            )
        except Exception as exc:
            err_msg = f"Không gọi được API submit của BAI.tools: {str(exc)}"
            await self.log_audit("ApiSubmit", "Failed", err_msg)
            return {
                "success": False,
                "response_data": None,
                "error_message": err_msg,
            }

        response_status = result.get("status")
        response_data = result.get("data")
        if result.get("ok") and isinstance(response_data, dict) and response_data.get("id"):
            submission_id = response_data.get("id")
            await self.log_audit("ApiSubmit", "Success", f"BAI.tools API trả về id={submission_id}.")
            return {
                "success": True,
                "response_data": self.result_parser.build_success_payload(
                    defaults,
                    submission_id=submission_id,
                ),
                "error_message": None,
            }

        err_msg = f"BAI.tools API trả về HTTP {response_status}."
        await self.log_audit("ApiSubmit", "Failed", err_msg)
        return {
            "success": False,
            "response_data": json.dumps(response_data, ensure_ascii=False) if response_data is not None else None,
            "error_message": err_msg,
        }

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=20.0)

        await self.log_audit("BrowserLaunch", "Running", "Đang khởi chạy Chrome để làm việc với BAI.tools...")

        async with async_playwright() as p:
            launch_kwargs = {
                "headless": not self._debug_enabled(),
                "slow_mo": self._debug_slow_mo_ms() or None,
                "args": ["--disable-blink-features=AutomationControlled"],
            }
            executable_path = self._chrome_executable_path()
            if executable_path:
                launch_kwargs["executable_path"] = executable_path
            else:
                launch_kwargs["channel"] = self._browser_channel()

            browser = await p.chromium.launch(**launch_kwargs)
            browser_helper = BrowserAutomationHelper(browser)
            self.form_mapper.bind_browser_helper(browser_helper) if hasattr(self.form_mapper, "bind_browser_helper") else None

            context = None
            try:
                context = await self.create_authenticated_context(browser)
                page = await context.new_page()

                await self.log_audit("NavigateSubmit", "Running", f"Đang điều hướng đến: {BAITOOLS_SUBMIT_URL}")
                try:
                    await page.goto(BAITOOLS_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(BAITOOLS_SUBMIT_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1000)
                if await self._pause_for_manual_oauth(page, "after-navigate"):
                    err_msg = "BAI.tools vẫn đang yêu cầu OAuth sau khi mở trang submit. Hãy hoàn tất đăng nhập rồi chạy lại."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                defaults = self.form_mapper.build_defaults(metadata, url)
                await self.log_audit("FormPreview", "Success", self.result_parser.format_preview(defaults))

                if mode.lower() == "preview":
                    return {
                        "success": True,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_preview_payload(defaults),
                        "error_message": None,
                    }

                if self._api_enabled(metadata):
                    api_result = await self._submit_via_api(page, defaults)
                    if api_result.get("success"):
                        return api_result
                    await self.log_audit(
                        "ApiSubmit",
                        "Failed",
                        api_result.get("error_message") or "BAI.tools API submit thất bại, fallback sang UI.",
                    )

                await self.log_audit("OpenForm", "Running", "Đang mở form Submit your AI Tool...")
                opened = await browser_helper.click_first_visible(
                    page,
                    [
                        "button:has-text('Submit your AI Tool')",
                        "button:has-text('Submit your AI tool')",
                        "text=Submit your AI Tool",
                        "text=Submit your AI tool",
                    ],
                )
                if not opened:
                    raise ValueError("Không tìm thấy nút Submit your AI Tool.")

                await page.wait_for_timeout(1000)
                await self.log_audit("FillForm", "Running", "Đang điền form BAI.tools...")
                await self.form_mapper.fill_form(page, browser_helper, defaults)

                if await self._pause_for_manual_oauth(page, "after-fill"):
                    err_msg = "BAI.tools vẫn đang yêu cầu OAuth sau khi điền form. Hãy hoàn tất đăng nhập rồi submit lại."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                await self.log_audit("Submit", "Running", "Đang chờ BAI.tools chuyển sang trang finish...")
                await retry_helper.run(lambda: page.wait_for_timeout(1000))

                finish_url, finish_text = await self._wait_for_finish_state(page, timeout_ms=20000)
                if not finish_url and not finish_text:
                    err_msg = "BAI.tools chưa trả về trang finish hoặc thông báo thành công."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit("Submit", "Success", f"BAI.tools đã hoàn tất submit. Thời gian: {duration}ms", duration)

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(
                        defaults,
                        finish_url=finish_url,
                        finish_text=finish_text,
                        submission_id=None,
                    ),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác BAI.tools: {str(e)}"
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
