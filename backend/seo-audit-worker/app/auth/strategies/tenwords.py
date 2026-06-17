from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from app.auth.base import BaseAuthStrategy
from app.core.crypto_helper import decrypt_credential
from app.session.storage_state_store import FileStorageStateStore


TENWORDS_BASE_URL = "https://portal.10words.io"
TENWORDS_LOGIN_URL = f"{TENWORDS_BASE_URL}/auth/login"
TENWORDS_SUBMISSIONS_URL = f"{TENWORDS_BASE_URL}/submissions"
DEFAULT_STORAGE_STATE_PATH = os.getenv(
    "TENWORDS_STORAGE_STATE_PATH",
    str(Path(__file__).resolve().parents[3] / ".playwright" / "tenwords_storage_state.json"),
)


class TenWordsAuthStrategy(BaseAuthStrategy):
    def __init__(self, handler: Any):
        super().__init__(handler)
        self.session_store = FileStorageStateStore(DEFAULT_STORAGE_STATE_PATH)

    def _parse_credential_payload(self, raw: str) -> Dict[str, str]:
        payload = (raw or "").strip()
        if not payload:
            return {}

        try:
            parsed = json.loads(payload)
            if isinstance(parsed, dict):
                return {
                    "email": (parsed.get("email") or parsed.get("username") or parsed.get("user") or "").strip(),
                    "password": (parsed.get("password") or parsed.get("pass") or "").strip(),
                }
        except Exception:
            pass

        if ":" in payload:
            email, password = payload.split(":", 1)
            return {"email": email.strip(), "password": password.strip()}

        return {"email": payload, "password": ""}

    async def _login_with_email_password(self, browser):
        if not self.handler.encrypted_credential or not self.handler.iv:
            raise ValueError("Thiếu credential mã hóa cho 10words. Hãy lưu email/password trước.")

        decrypted_str = decrypt_credential(self.handler.encrypted_credential, self.handler.iv)
        creds = self._parse_credential_payload(decrypted_str)
        email = creds.get("email", "")
        password = creds.get("password", "")

        if not email or not password:
            raise ValueError("Credential 10words không chứa đủ email/password.")

        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        try:
            await self.handler.log_audit("LoginCheck", "Running", "Đang đăng nhập 10words bằng email/password...")
            await page.goto(TENWORDS_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)

            email_selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[autocomplete='email']",
                "input[placeholder*='email']",
            ]
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[autocomplete='current-password']",
            ]

            email_filled = False
            for selector in email_selectors:
                locator = page.locator(selector)
                if await locator.count() == 0:
                    continue
                try:
                    await locator.first.fill(email)
                    email_filled = True
                    break
                except Exception:
                    continue

            password_filled = False
            for selector in password_selectors:
                locator = page.locator(selector)
                if await locator.count() == 0:
                    continue
                try:
                    await locator.first.fill(password)
                    password_filled = True
                    break
                except Exception:
                    continue

            if not email_filled or not password_filled:
                raise ValueError("Không tìm thấy field đăng nhập email/password của 10words.")

            submit_selectors = [
                "button[type='submit']",
                "button:has-text('Sign in')",
                "button:has-text('Login')",
                "button:has-text('Log in')",
                "input[type='submit']",
            ]
            submitted = False
            for selector in submit_selectors:
                locator = page.locator(selector)
                if await locator.count() == 0:
                    continue
                try:
                    await locator.first.click(no_wait_after=True)
                    submitted = True
                    break
                except Exception:
                    continue

            if not submitted:
                raise ValueError("Không tìm thấy nút Sign in/Login của 10words.")

            await page.wait_for_timeout(1500)
            await page.goto(TENWORDS_SUBMISSIONS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1000)

            await context.storage_state(path=str(self.session_store.storage_state_path))
            await self.handler.log_audit(
                "SessionBootstrap",
                "Success",
                f"Đã login 10words và lưu storage_state tại {self.session_store.storage_state_path}."
            )
            return context
        except Exception:
            await context.close()
            raise

    async def ensure_authenticated(self, browser):
        if self.session_store.exists():
            context = await browser.new_context(**self.session_store.context_kwargs())
            page = await context.new_page()
            try:
                await self.handler.log_audit(
                    "SessionBootstrap",
                    "Running",
                    f"Đang load storage_state 10words từ {self.session_store.storage_state_path}..."
                )
                await page.goto(TENWORDS_SUBMISSIONS_URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1000)
                if "auth/login" in (page.url or ""):
                    await context.close()
                else:
                    await self.handler.log_audit(
                        "SessionBootstrap",
                        "Success",
                        "Đã load storage_state 10words thành công."
                    )
                    return context
            except Exception:
                await context.close()

        return await self._login_with_email_password(browser)
