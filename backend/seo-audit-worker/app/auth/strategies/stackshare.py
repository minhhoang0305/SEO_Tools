import json
from typing import Any, Dict, List

from app.auth.base import BaseAuthStrategy
from app.core.crypto_helper import decrypt_credential


STACKSHARE_BASE_URL = "https://stackshare.io"
STACKSHARE_LOGIN_URL = f"{STACKSHARE_BASE_URL}/login"


class StackShareAuthStrategy(BaseAuthStrategy):
    def _parse_cookies(self, raw_cookies: str) -> List[Dict[str, Any]]:
        try:
            cookies_list = json.loads(raw_cookies)
            if not isinstance(cookies_list, list):
                cookies_list = [cookies_list]
            return cookies_list
        except json.JSONDecodeError:
            return [
                {
                    "name": "__Secure-authjs.session-token",
                    "value": raw_cookies.strip(),
                    "domain": ".stackshare.io",
                    "path": "/"
                }
            ]

    async def _load_credential_cookies(self) -> List[Dict[str, Any]]:
        encrypted_credential = self.handler.encrypted_credential
        iv = self.handler.iv

        if not encrypted_credential or not iv:
            return []

        await self.handler.log_audit(
            "DecryptCredential",
            "Running",
            "Đang giải mã session cookies từ database..."
        )
        decrypted_str = decrypt_credential(encrypted_credential, iv)
        if not decrypted_str:
            await self.handler.log_audit(
                "DecryptCredential",
                "Failed",
                "Không thể giải mã credentials."
            )
            return []

        cookies_list = self._parse_cookies(decrypted_str)
        await self.handler.log_audit(
            "DecryptCredential",
            "Success",
            f"Đã giải mã thành công {len(cookies_list)} cookies."
        )
        return cookies_list

    async def ensure_authenticated(self, browser):
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        context_args.update(self.session_store.context_kwargs())

        context = await browser.new_context(**context_args)

        cookies_list = await self._load_credential_cookies()
        if cookies_list:
            await context.add_cookies(cookies_list)
        else:
            await self.handler.log_audit(
                "SessionBootstrap",
                "Running",
                "Không có cookie lưu sẵn, Playwright sẽ thử dùng storage state hiện có."
            )

        page = await context.new_page()
        try:
            await self.handler.log_audit(
                "LoginCheck",
                "Running",
                "Đang truy cập StackShare và kiểm tra trạng thái Session..."
            )
            await page.goto(STACKSHARE_LOGIN_URL, wait_until="networkidle", timeout=30000)

            signin_button = page.locator(
                "a:has-text('Sign In'), button:has-text('Sign In'), a[href='/login']"
            )
            is_logged_out = await signin_button.count() > 0 and await signin_button.first.is_visible()

            if is_logged_out:
                if cookies_list or self.session_store.exists():
                    err_msg = "Session StackShare hết hạn hoặc không hợp lệ. Vui lòng đồng bộ lại session."
                else:
                    err_msg = (
                        "Playwright chưa có session StackShare hợp lệ. "
                        "Cần storage_state hoặc cookie hợp lệ."
                    )
                await self.handler.log_audit("LoginCheck", "Failed", err_msg)
                raise ValueError(err_msg)

            await self.session_store.save(context)
            await self.handler.log_audit(
                "SessionBootstrap",
                "Success",
                "Đã lưu storage_state của StackShare để tái sử dụng cho các lần chạy sau."
            )
            await self.handler.log_audit(
                "LoginCheck",
                "Success",
                "Xác thực Session thành công (Đã đăng nhập)."
            )
            return context
        except Exception:
            await context.close()
            raise
