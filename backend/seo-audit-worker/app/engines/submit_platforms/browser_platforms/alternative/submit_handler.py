from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path
from shutil import which
from typing import Any, Dict

from playwright.async_api import async_playwright

from app.auth.strategies.alternative import AlternativeAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.retry_timeout import RetryTimeoutHandler

from .constants import ALTERNATIVE_FALSE_POSITIVE_PATTERNS, ALTERNATIVE_SUCCESS_PATTERNS, ALTERNATIVE_SUBMIT_URL
from .form_mapper import AlternativeFormMapper
from .result_parser import AlternativeResultParser


class AlternativeSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = AlternativeAuthStrategy

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = AlternativeFormMapper(self)
        self.result_parser = AlternativeResultParser()

    def _debug_enabled(self) -> bool:
        return (os.getenv("ALTERNATIVE_DEBUG_HEADFUL", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _debug_slow_mo_ms(self) -> int:
        raw_value = (os.getenv("ALTERNATIVE_DEBUG_SLOWMO_MS", "") or "").strip()
        if not raw_value:
            return 0
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _debug_artifact_dir(self) -> Path:
        raw_path = (os.getenv("ALTERNATIVE_DEBUG_ARTIFACT_DIR", "") or "").strip()
        if raw_path:
            return Path(raw_path).expanduser()
        return Path(__file__).resolve().parents[5] / ".playwright" / "alternative-debug"

    def _debug_dump(self, title: str, payload: Any) -> None:
        if not self._debug_enabled():
            return
        print(f"\n[AlternativeDebug] {title}:")
        if isinstance(payload, (dict, list)):
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(payload)

    def _chrome_executable_path(self) -> str | None:
        raw_value = (os.getenv("ALTERNATIVE_CHROME_EXECUTABLE_PATH", "") or "").strip()
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

    async def _wait_for_success(self, page, timeout_ms: int = 15000) -> bool:
        deadline = time.time() + (timeout_ms / 1000.0)
        while time.time() < deadline:
            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
            except Exception:
                body_text = ""
            if any(pattern in body_text for pattern in ALTERNATIVE_FALSE_POSITIVE_PATTERNS):
                await page.wait_for_timeout(500)
                continue
            if any(pattern in body_text for pattern in ALTERNATIVE_SUCCESS_PATTERNS):
                return True
            await page.wait_for_timeout(500)
        return False

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=20.0)

        await self.log_audit("BrowserLaunch", "Running", "Đang khởi chạy Chrome để làm việc với Alternative...")
        self._debug_dump("Input", {"url": url, "mode": mode, "metadata": metadata})

        async with async_playwright() as p:
            launch_kwargs = {
                "headless": not self._debug_enabled(),
                "slow_mo": self._debug_slow_mo_ms() or None,
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

                await self.log_audit("NavigateSubmit", "Running", f"Đang điều hướng đến: {ALTERNATIVE_SUBMIT_URL}")
                try:
                    await page.goto(ALTERNATIVE_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(ALTERNATIVE_SUBMIT_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1200)

                defaults = self.form_mapper.build_defaults(metadata, url)
                self._debug_dump("MappedDefaults", defaults)
                await self.log_audit("FormPreview", "Success", self.result_parser.format_preview(defaults))

                if mode.lower() == "preview":
                    return {
                        "success": True,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_preview_payload(defaults),
                        "error_message": None,
                    }

                await self.log_audit("WizardStep", "Running", "Đang điền bước đầu của Alternative...")
                self._debug_dump("WizardStepPayload", defaults)
                await self.form_mapper.fill_initial_wizard_step(page, browser_helper, defaults)
                await browser_helper.wait_for_text_visible(page, "body", "Short Description", timeout=15000)

                await self.log_audit("FillForm", "Running", "Đang điền form Alternative...")
                self._debug_dump("FillFormPayload", defaults)
                await self.form_mapper.fill_form(page, browser_helper, defaults)

                if self._debug_enabled():
                    artifact_dir = self._debug_artifact_dir()
                    artifact_dir.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=str(artifact_dir / "after-fill.png"), full_page=True)

                await page.wait_for_timeout(1000)
                await retry_helper.run(lambda: browser_helper.wait_for_button_enabled(page, "button", "Submit", timeout=15000))

                submit_button = page.get_by_role("button", name=re.compile(r"Submit", re.IGNORECASE))
                if await submit_button.count() == 0:
                    raise ValueError("Không tìm thấy nút Submit trên Alternative.")

                await submit_button.first.click()
                await self.log_audit("Submit", "Running", "Đã bấm Submit. Đang chờ phản hồi của Alternative...")

                if not await self._wait_for_success(page, timeout_ms=15000):
                    err_msg = "Đã bấm Submit nhưng chưa thấy xác nhận rõ ràng từ Alternative; coi như đang chờ xác nhận."
                    await self.log_audit("Submit", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit("Submit", "Success", f"Đã submit Alternative thành công. Thời gian: {duration}ms", duration)

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(defaults, final_url=page.url),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác Alternative: {str(e)}"
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
