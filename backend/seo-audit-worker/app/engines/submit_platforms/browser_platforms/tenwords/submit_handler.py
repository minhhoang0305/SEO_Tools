from __future__ import annotations

import json
import os
import time
from typing import Any, Dict
from pathlib import Path
from shutil import which

from playwright.async_api import async_playwright

from app.auth.strategies.tenwords import TenWordsAuthStrategy
from app.core.crypto_helper import decrypt_credential
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.api_client import ApiClientHelper
from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.retry_timeout import RetryTimeoutHandler

from .constants import TENWORDS_API_URL, TENWORDS_SUBMISSIONS_URL, TENWORDS_SUBMIT_URL, TENWORDS_SUCCESS_PATTERNS
from .form_mapper import TenWordsFormMapper
from .result_parser import TenWordsResultParser


class TenWordsSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = TenWordsAuthStrategy

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = TenWordsFormMapper(self)
        self.result_parser = TenWordsResultParser()

    def _debug_enabled(self) -> bool:
        return (os.getenv("TENWORDS_DEBUG_HEADFUL", "") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _debug_slow_mo_ms(self) -> int:
        raw_value = (os.getenv("TENWORDS_DEBUG_SLOWMO_MS", "") or "").strip()
        if not raw_value:
            return 0
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _chrome_executable_path(self) -> str | None:
        raw_value = (os.getenv("TENWORDS_CHROME_EXECUTABLE_PATH", "") or "").strip()
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

    def _profile_dir(self) -> Path:
        raw_value = (os.getenv("TENWORDS_PROFILE_DIR", "") or "").strip()
        if raw_value:
            return Path(raw_value).expanduser()
        return Path(__file__).resolve().parents[5] / ".playwright" / "tenwords_chrome_profile"

    def _api_token(self, metadata: Dict[str, Any]) -> str:
        for candidate in (
            metadata.get("TenWordsApiToken"),
            metadata.get("ApiToken"),
            self.platform_info.get("ApiToken"),
            os.getenv("TENWORDS_API_TOKEN", ""),
        ):
            raw_value = (candidate or "").strip()
            if raw_value:
                return raw_value

        if self.encrypted_credential and self.iv:
            decrypted = decrypt_credential(self.encrypted_credential, self.iv).strip()
            if decrypted:
                try:
                    parsed = json.loads(decrypted)
                    if isinstance(parsed, dict):
                        for key in ("token", "api_token", "auth_token"):
                            token = (parsed.get(key) or "").strip()
                            if token:
                                return token
                except Exception:
                    pass
        return ""

    def _api_category_id(self, data: Dict[str, str], metadata: Dict[str, Any]) -> int:
        raw_value = metadata.get("TenWordsCategoryId") or data.get("category_id") or data.get("category")
        try:
            return int(raw_value)
        except Exception:
            pass

        category_value = (data.get("category") or "").strip().lower()
        mapping = {
            "website": 1,
            "saas": 2,
            "mobile app": 3,
            "newsletter": 4,
            "other": 5,
        }
        return mapping.get(category_value, 1)

    async def _submit_via_api(self, url: str, metadata: Dict[str, Any], defaults: Dict[str, str]) -> Dict[str, Any]:
        token = self._api_token(metadata)
        if not token:
            return {
                "success": False,
                "response_data": None,
                "error_message": "Thiếu TENWORDS_API_TOKEN hoặc token 10words trong credential/metadata.",
            }

        payload = {
            "name": defaults.get("project_name", ""),
            "category": self._api_category_id(defaults, metadata),
            "description": defaults.get("description", ""),
            "link": defaults.get("project_url", url),
            "twitter": defaults.get("twitter_handle", ""),
            "newsletter": 0 if (defaults.get("newsletter") or "").strip().lower() in {"no thanks", "no", "false", "0"} else 1,
        }

        headers = {
            "Authorization": f"Token {token}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://portal.10words.io",
            "Referer": "https://portal.10words.io/",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
            ),
        }

        api_client = ApiClientHelper(timeout=20.0, follow_redirects=True)
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=20.0)

        await self.log_audit(
            "ApiSubmit",
            "Running",
            f"Đang gửi API submit tới 10words: {TENWORDS_API_URL}. Payload: {payload}",
        )

        response = await retry_helper.run(
            lambda: api_client.post(TENWORDS_API_URL, headers=headers, json=payload)
        )

        response_json = response.json_data
        if response.status_code in {200, 201}:
            await self.log_audit(
                "ApiSubmit",
                "Success",
                f"10words API trả về HTTP {response.status_code}.",
            )
            return {
                "success": True,
                "response_data": response_json or response.text,
                "error_message": None,
            }

        err_msg = f"10words API trả về HTTP {response.status_code}."
        await self.log_audit("ApiSubmit", "Failed", err_msg)
        return {
            "success": False,
            "response_data": response_json or response.text,
            "error_message": err_msg,
        }

    async def _wait_for_success(self, page, timeout_ms: int = 15000) -> tuple[str, str]:
        deadline = time.time() + (timeout_ms / 1000.0)
        while time.time() < deadline:
            current_url = page.url or ""
            if "/submissions/submitted/" in current_url.lower():
                return current_url, ""

            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip()
            except Exception:
                body_text = ""
            if any(pattern in body_text.lower() for pattern in TENWORDS_SUCCESS_PATTERNS):
                return current_url, body_text

            await page.wait_for_timeout(500)

        return page.url or "", ""

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=20.0)

        await self.log_audit("BrowserLaunch", "Running", "Đang khởi chạy Chrome để làm việc với 10words...")

        defaults = self.form_mapper.build_defaults(metadata, url)
        await self.log_audit("FormPreview", "Success", self.result_parser.format_preview(defaults))

        if mode.lower() == "preview":
            return {
                "success": True,
                "requires_manual_action": True,
                "response_data": self.result_parser.build_preview_payload(defaults),
                "error_message": None,
            }

        api_token = self._api_token(metadata)
        if api_token:
            api_result = await self._submit_via_api(url, metadata, defaults)
            if api_result.get("success"):
                return api_result
            await self.log_audit(
                "ApiSubmit",
                "Failed",
                api_result.get("error_message") or "10words API submit thất bại.",
            )

        async with async_playwright() as p:

            profile_dir = self._profile_dir()
            profile_dir.mkdir(parents=True, exist_ok=True)
            launch_kwargs = {
                "user_data_dir": str(profile_dir),
                "headless": not self._debug_enabled(),
                "slow_mo": self._debug_slow_mo_ms() or None,
                "args": ["--disable-blink-features=AutomationControlled"],
            }
            chrome_path = self._chrome_executable_path()
            if chrome_path:
                launch_kwargs["executable_path"] = chrome_path
            else:
                launch_kwargs["channel"] = "chrome"

            context = await p.chromium.launch_persistent_context(**launch_kwargs)
            browser_helper = BrowserAutomationHelper(context.browser)

            try:
                page = context.pages[0] if context.pages else await context.new_page()

                await self.log_audit("NavigateSubmit", "Running", f"Đang điều hướng đến: {TENWORDS_SUBMISSIONS_URL}")
                try:
                    await page.goto(TENWORDS_SUBMISSIONS_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(TENWORDS_SUBMISSIONS_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1000)
                if "auth/login" in (page.url or ""):
                    await self.log_audit(
                        "NavigateSubmit",
                        "Running",
                        "Session 10words chưa vào được submissions, thử mở trực tiếp trang submit..."
                    )
                    try:
                        await page.goto(TENWORDS_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        await page.goto(TENWORDS_SUBMIT_URL, wait_until="load", timeout=30000)
                await page.wait_for_timeout(1000)

                opened = await browser_helper.click_first_visible(
                    page,
                    [
                        "button:has-text('Submit another Project')",
                        "button:has-text('Submit Project')",
                        "text=Submit another Project",
                    ],
                )
                if opened:
                    await page.wait_for_timeout(1000)

                if "submissions/submit" not in (page.url or ""):
                    try:
                        await page.goto(TENWORDS_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        await page.goto(TENWORDS_SUBMIT_URL, wait_until="load", timeout=30000)
                await page.wait_for_timeout(1000)

                await self.log_audit("FillForm", "Running", "Đang điền form 10words...")
                await self.form_mapper.fill_form(page, browser_helper, defaults)

                await self.log_audit("Submit", "Running", "Đang chờ 10words xử lý submit...")
                await retry_helper.run(lambda: page.wait_for_timeout(1000))

                finish_url, finish_text = await self._wait_for_success(page, timeout_ms=20000)
                duration = int((time.time() - start_time) * 1000)

                if not finish_url and not finish_text:
                    err_msg = "10words chưa trả về trang thành công hoặc thông báo xác nhận."
                    await self.log_audit("Submit", "Failed", err_msg, duration)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                await self.log_audit("Submit", "Success", f"10words đã hoàn tất submit. Thời gian: {duration}ms", duration)
                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(defaults, finish_url=finish_url),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác 10words: {str(e)}"
                await self.log_audit("Submit", "Failed", err_msg, duration)
                return {
                    "success": False,
                    "response_data": None,
                    "error_message": err_msg,
                }
            finally:
                if context is not None:
                    await context.close()
