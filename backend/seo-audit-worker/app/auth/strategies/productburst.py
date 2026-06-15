from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.auth.base import BaseAuthStrategy
from app.session.storage_state_store import FileStorageStateStore


PRODUCTBURST_BASE_URL = "https://productburst.com"
PRODUCTBURST_AUTH_URL = f"{PRODUCTBURST_BASE_URL}/auth"
PRODUCTBURST_PRE_LAUNCH_URL = f"{PRODUCTBURST_BASE_URL}/pre-launch"
DEFAULT_STORAGE_STATE_PATH = os.getenv(
    "PRODUCTBURST_STORAGE_STATE_PATH",
    str(Path(__file__).resolve().parents[3] / ".playwright" / "productburst_storage_state.json"),
)


class ProductBurstAuthStrategy(BaseAuthStrategy):
    def __init__(self, handler: Any):
        super().__init__(handler)
        self.session_store = FileStorageStateStore(DEFAULT_STORAGE_STATE_PATH)

    def _looks_like_auth_url(self, current_url: str) -> bool:
        path = urlparse(current_url).path.lower()
        return "/auth" in path or "/login" in path or "/signin" in path or "/sign-in" in path

    async def _has_visible_login_form(self, page) -> bool:
        selectors = [
            "input[type='email']",
            "input[type='password']",
            "button:has-text('Continue with Google')",
            "button:has-text('Sign in')",
            "button:has-text('Login')",
            "a:has-text('Create a free account')",
        ]

        for selector in selectors:
            locator = page.locator(selector)
            try:
                if await locator.count() > 0 and await locator.first.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def _materialize_storage_state_file(self) -> bool:
        if self.session_store.exists():
            return True

        await self.handler.log_audit(
            "LoginCheck",
            "Failed",
            "Chưa có storage_state của ProductBurst. Hãy login local bằng Google hoặc Email/Password rồi upload file session."
        )
        return False

    async def ensure_authenticated(self, browser):
        if not await self._materialize_storage_state_file():
            raise ValueError("Chưa có storage_state của ProductBurst. Hãy connect account lại.")

        context = await browser.new_context(**self.session_store.context_kwargs())
        page = await context.new_page()

        try:
            await self.handler.log_audit(
                "LoginCheck",
                "Running",
                "Đang truy cập ProductBurst để kiểm tra session đã lưu..."
            )
            try:
                await page.goto(PRODUCTBURST_PRE_LAUNCH_URL, wait_until="domcontentloaded", timeout=30000)
            except Exception:
                await page.goto(PRODUCTBURST_PRE_LAUNCH_URL, wait_until="load", timeout=30000)

            await page.wait_for_timeout(1500)
            current_url = page.url
            login_form_visible = await self._has_visible_login_form(page)

            await self.handler.log_audit(
                "LoginCheck",
                "Running",
                f"URL sau khi truy cập: {current_url}. Login form visible: {login_form_visible}."
            )

            if self._looks_like_auth_url(current_url) or login_form_visible:
                err_msg = "Session ProductBurst hết hạn hoặc không hợp lệ. Hãy Connect Account lại."
                await self.handler.log_audit("LoginCheck", "Failed", err_msg)
                raise ValueError(err_msg)

            await self.handler.log_audit(
                "SessionBootstrap",
                "Success",
                "Đã load storage_state và xác thực session ProductBurst thành công."
            )
            return context
        except Exception:
            await context.close()
            raise
