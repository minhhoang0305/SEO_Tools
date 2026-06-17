from __future__ import annotations

import asyncio
import os
import re
import time
from shutil import which
from pathlib import Path
from typing import Any, Dict

from playwright.async_api import async_playwright

from app.auth.strategies.futuretools import FutureToolsAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.retry_timeout import RetryTimeoutHandler

from .constants import FUTURETOOLS_SUBMIT_URL, FUTURETOOLS_SUCCESS_PATTERNS
from .form_mapper import FutureToolsFormMapper
from .result_parser import FutureToolsResultParser


class FutureToolsSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = FutureToolsAuthStrategy
    HUMAN_VERIFICATION_PATTERNS = (
        "verify you are human",
        "human verification",
        "captcha",
        "cloudflare",
        "challenge",
    )

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = FutureToolsFormMapper(self)
        self.result_parser = FutureToolsResultParser()

    def _debug_enabled(self) -> bool:
        return (os.getenv("FUTURETOOLS_DEBUG_HEADFUL", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _debug_slow_mo_ms(self) -> int:
        raw_value = (os.getenv("FUTURETOOLS_DEBUG_SLOWMO_MS", "") or "").strip()
        if not raw_value:
            return 0
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _debug_artifact_dir(self) -> Path:
        raw_path = (os.getenv("FUTURETOOLS_DEBUG_ARTIFACT_DIR", "") or "").strip()
        if raw_path:
            return Path(raw_path).expanduser()
        return Path(__file__).resolve().parents[5] / ".playwright" / "futuretools-debug"

    def _browser_channel(self) -> str:
        raw_value = (os.getenv("FUTURETOOLS_BROWSER_CHANNEL", "") or "").strip()
        return raw_value or "chrome"

    def _chrome_executable_path(self) -> str | None:
        raw_value = (os.getenv("FUTURETOOLS_CHROME_EXECUTABLE_PATH", "") or "").strip()
        if raw_value and Path(raw_value).expanduser().exists():
            return raw_value

        candidates = [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
            Path.home() / "Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        for binary in ("google-chrome", "google-chrome-stable", "chrome", "chromium", "chromium-browser"):
            found = which(binary)
            if found and Path(found).exists():
                return found

        return None

    def _profile_dir(self) -> Path | None:
        raw_value = (os.getenv("FUTURETOOLS_PROFILE_DIR", "") or "").strip()
        if not raw_value:
            return None
        return Path(raw_value).expanduser()

    def _wait_for_manual_verification_enabled(self) -> bool:
        return (os.getenv("FUTURETOOLS_WAIT_FOR_MANUAL_VERIFICATION", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    async def _detect_human_verification(self, page) -> bool:
        try:
            body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
        except Exception:
            body_text = ""

        if not body_text:
            return False

        return any(pattern in body_text for pattern in self.HUMAN_VERIFICATION_PATTERNS)

    async def _pause_for_manual_verification(self, page, stage: str) -> bool:
        if not await self._detect_human_verification(page):
            return False

        message = (
            f"FutureTools đang yêu cầu xác thực người thật ở bước {stage}. "
            "Hãy hoàn tất xác thực trong Chrome rồi nhấn Enter ở terminal để tiếp tục..."
        )
        await self.log_audit("ManualAction", "Running", message)

        if self._debug_enabled():
            artifact_dir = self._debug_artifact_dir()
            artifact_dir.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(artifact_dir / f"human-verification-{stage}.png"), full_page=True)

        if not self._wait_for_manual_verification_enabled():
            return True

        await asyncio.to_thread(input, f"{message}\n")
        await page.wait_for_timeout(1000)
        return await self._detect_human_verification(page)

    async def _wait_for_submission_confirmation(self, page, timeout_ms: int = 12000):
        deadline = time.time() + (timeout_ms / 1000.0)

        while time.time() < deadline:
            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
            except Exception:
                body_text = ""

            for pattern in FUTURETOOLS_SUCCESS_PATTERNS:
                if pattern in body_text:
                    return {
                        "source": "body",
                        "matched_text": pattern,
                    }

            try:
                current_url = page.url or ""
                if current_url != FUTURETOOLS_SUBMIT_URL and "futuretools.io" in current_url:
                    return {
                        "source": "url",
                        "matched_text": current_url,
                    }
            except Exception:
                pass

            await page.wait_for_timeout(500)

        return None

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=15.0)

        await self.log_audit(
            "BrowserLaunch",
            "Running",
            f"Đang khởi chạy Chrome để làm việc với FutureTools..."
        )

        async with async_playwright() as p:
            profile_dir = self._profile_dir()
            browser = None
            browser_context = None
            executable_path = self._chrome_executable_path()
            await self.log_audit(
                "BrowserLaunch",
                "Running",
                (
                    f"Chrome path: {executable_path or '[channel chrome]'}; "
                    f"profile: {profile_dir or '[none]'}"
                ),
            )
            if profile_dir is not None:
                profile_dir.mkdir(parents=True, exist_ok=True)
                launch_kwargs = {
                    "user_data_dir": str(profile_dir),
                    "headless": not self._debug_enabled(),
                    "slow_mo": self._debug_slow_mo_ms() or None,
                    "viewport": {"width": 1280, "height": 900},
                    "args": ["--disable-blink-features=AutomationControlled"],
                }
                if executable_path:
                    launch_kwargs["executable_path"] = executable_path
                else:
                    launch_kwargs["channel"] = self._browser_channel()

                browser_context = await p.chromium.launch_persistent_context(**launch_kwargs)
                browser_helper = BrowserAutomationHelper(browser_context)
            else:
                launch_kwargs = {
                    "headless": not self._debug_enabled(),
                    "slow_mo": self._debug_slow_mo_ms() or None,
                    "args": ["--disable-blink-features=AutomationControlled"],
                }
                if executable_path:
                    launch_kwargs["executable_path"] = executable_path
                else:
                    launch_kwargs["channel"] = self._browser_channel()

                browser = await p.chromium.launch(**launch_kwargs)
                browser_helper = BrowserAutomationHelper(browser)

            context = None
            try:
                if profile_dir is not None:
                    context = browser_context
                    page = context.pages[0] if context.pages else await context.new_page()
                else:
                    context = await self.create_authenticated_context(browser)
                    page = await context.new_page()

                await self.log_audit(
                    "NavigateSubmit",
                    "Running",
                    f"Đang điều hướng đến: {FUTURETOOLS_SUBMIT_URL}"
                )
                try:
                    await page.goto(FUTURETOOLS_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(FUTURETOOLS_SUBMIT_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1000)
                if await self._pause_for_manual_verification(page, "after-navigate"):
                    err_msg = "FutureTools vẫn đang yêu cầu xác thực người thật. Hãy hoàn tất challenge rồi chạy lại submit."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                defaults = self.form_mapper.build_defaults(metadata, url)
                await self.log_audit(
                    "FormPreview",
                    "Success",
                    self.result_parser.format_preview(defaults)
                )

                if mode.lower() == "preview":
                    return {
                        "success": True,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_preview_payload(defaults),
                        "error_message": None,
                    }

                await self.log_audit(
                    "FillForm",
                    "Running",
                    "Đang điền form FutureTools..."
                )
                await self.form_mapper.fill_form(page, browser_helper, defaults)

                if await self._pause_for_manual_verification(page, "after-fill"):
                    err_msg = "FutureTools vẫn đang yêu cầu xác thực người thật sau khi điền form. Hãy hoàn tất challenge rồi nhấn submit thủ công nếu cần."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                if self._debug_enabled():
                    artifact_dir = self._debug_artifact_dir()
                    artifact_dir.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=str(artifact_dir / "after-fill.png"), full_page=True)

                await page.wait_for_timeout(1000)
                await retry_helper.run(
                    lambda: browser_helper.wait_for_button_enabled(page, "button", "Submit Tool", timeout=15000)
                )

                submit_button = page.get_by_role("button", name=re.compile(r"Submit Tool", re.IGNORECASE))
                if await submit_button.count() == 0:
                    raise ValueError("Không tìm thấy nút Submit Tool trên FutureTools.")

                await submit_button.first.click()

                await self.log_audit(
                    "Submit",
                    "Running",
                    "Đã bấm Submit Tool. Đang chờ phản hồi của FutureTools..."
                )

                if await self._pause_for_manual_verification(page, "after-submit"):
                    err_msg = "FutureTools đang yêu cầu xác thực người thật sau khi submit. Hãy hoàn tất challenge trong Chrome rồi thử lại nếu cần."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                confirmation = await self._wait_for_submission_confirmation(page, timeout_ms=15000)
                if not confirmation:
                    err_msg = (
                        "Đã bấm Submit nhưng chưa xác nhận được phản hồi thành công từ FutureTools."
                    )
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit(
                    "Submit",
                    "Success",
                    (
                        "Đã nhận được xác nhận từ FutureTools "
                        f"(nguồn: {confirmation.get('source')}, khớp: {confirmation.get('matched_text')}). "
                        f"Thời gian: {duration}ms"
                    ),
                    duration,
                )

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(
                        defaults,
                        final_url=page.url,
                    ),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác FutureTools: {str(e)}"
                await self.log_audit("Submit", "Failed", err_msg, duration)
                return {
                    "success": False,
                    "response_data": None,
                    "error_message": err_msg,
                }
            finally:
                if context is not None:
                    await context.close()
                if browser is not None:
                    await browser.close()
