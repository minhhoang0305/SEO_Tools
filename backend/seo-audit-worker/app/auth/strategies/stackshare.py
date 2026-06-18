import json
from typing import Any, Dict, List
from urllib.parse import urlparse

from app.auth.base import BaseAuthStrategy
from app.core.crypto_helper import decrypt_credential


STACKSHARE_BASE_URL = "https://stackshare.io"
STACKSHARE_LOGIN_URL = STACKSHARE_BASE_URL


class StackShareAuthStrategy(BaseAuthStrategy):
    def _base_context_args(self) -> Dict[str, Any]:
        return {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
            },
        }

    def _stealth_script(self) -> str:
        return r"""
(() => {
  const define = (object, property, getter) => {
    try {
      Object.defineProperty(object, property, {
        get: getter,
        configurable: true,
      });
    } catch (error) {}
  };

  define(Navigator.prototype, 'webdriver', () => undefined);
  define(Navigator.prototype, 'platform', () => 'Win32');
  define(Navigator.prototype, 'hardwareConcurrency', () => 8);
  define(Navigator.prototype, 'deviceMemory', () => 8);
  define(Navigator.prototype, 'languages', () => ['en-US', 'en']);

  try {
    window.chrome = window.chrome || {};
    window.chrome.runtime = window.chrome.runtime || {};
  } catch (error) {}

  try {
    const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
    if (originalQuery) {
      window.navigator.permissions.query = (parameters) => (
        parameters && parameters.name === 'notifications'
          ? Promise.resolve({ state: Notification.permission })
          : originalQuery(parameters)
      );
    }
  } catch (error) {}

  try {
    const pluginArray = [
      {
        name: 'Chrome PDF Plugin',
        filename: 'internal-pdf-viewer',
        description: 'Portable Document Format',
      },
      {
        name: 'Chrome PDF Viewer',
        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
        description: '',
      },
      {
        name: 'Native Client',
        filename: 'internal-nacl-plugin',
        description: '',
      },
    ];

    const mimeTypes = [
      {
        type: 'application/pdf',
        suffixes: 'pdf',
        description: '',
        enabledPlugin: pluginArray[0],
      },
    ];

    define(Navigator.prototype, 'plugins', () => pluginArray);
    define(Navigator.prototype, 'mimeTypes', () => mimeTypes);
  } catch (error) {}
})();
"""

    async def _apply_stealth(self, context, page) -> None:
        await context.add_init_script(self._stealth_script())

        try:
            from playwright_stealth import stealth_async  # type: ignore

            await stealth_async(page)
        except Exception:
            pass

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

    async def _load_storage_state_payload(self) -> str:
        encrypted_credential = self.handler.encrypted_credential
        iv = self.handler.iv

        if not encrypted_credential or not iv:
            return ""

        await self.handler.log_audit(
            "DecryptCredential",
            "Running",
            "Đang giải mã storage_state StackShare từ database..."
        )
        decrypted_str = decrypt_credential(encrypted_credential, iv)
        if not decrypted_str:
            await self.handler.log_audit(
                "DecryptCredential",
                "Failed",
                "Không thể giải mã storage_state."
            )
            return ""

        await self.handler.log_audit(
            "DecryptCredential",
            "Success",
            "Đã giải mã storage_state StackShare thành công."
        )
        return decrypted_str

    def _normalize_storage_state_json(self, payload: str) -> str:
        raw = (payload or "").strip()
        if not raw:
            return ""

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            cookies_list = self._parse_cookies(raw)
            parsed = {"cookies": cookies_list, "origins": []}
            return json.dumps(parsed, ensure_ascii=False, indent=2)

        if isinstance(parsed, list):
            parsed = {"cookies": parsed, "origins": []}
        elif isinstance(parsed, dict):
            parsed.setdefault("cookies", [])
            parsed.setdefault("origins", [])
        else:
            parsed = {"cookies": [], "origins": []}

        return json.dumps(parsed, ensure_ascii=False, indent=2)

    async def _materialize_storage_state_file(self) -> bool:
        if self.session_store.exists():
            return True

        decrypted_payload = await self._load_storage_state_payload()
        if not decrypted_payload:
            return False

        normalized_payload = self._normalize_storage_state_json(decrypted_payload)
        if not normalized_payload:
            return False

        self.session_store.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_store.storage_state_path.write_text(normalized_payload, encoding="utf-8")
        await self.handler.log_audit(
            "SessionBootstrap",
            "Success",
            f"Đã materialize storage_state về {self.session_store.storage_state_path}."
        )
        return True

    def _looks_like_login_url(self, current_url: str) -> bool:
        path = urlparse(current_url).path.lower()
        return "/login" in path or "/signin" in path or "/sign-in" in path

    async def _has_visible_login_form(self, page) -> bool:
        login_form_selectors = [
            "input[type='password']",
            "input[type='email']",
            "button:has-text('Sign in')",
            "button:has-text('Sign In')",
            "button:has-text('Continue with Google')",
            "button:has-text('Continue with GitHub')",
            "button:has-text('Sign in with Google')",
            "button:has-text('Sign in with GitHub')",
            "a:has-text('Sign in')",
            "a:has-text('Sign In')",
            "a:has-text('Continue with Google')",
            "a:has-text('Continue with GitHub')",
            "a:has-text('Sign in with Google')",
            "a:has-text('Sign in with GitHub')",
            "a[href='/login']",
        ]

        for selector in login_form_selectors:
            locator = page.locator(selector)
            try:
                if await locator.count() > 0 and await locator.first.is_visible():
                    return True
            except Exception:
                continue
        return False

    async def _save_session(self, context) -> None:
        await self.session_store.save(context)
        await self.handler.log_audit(
            "SessionBootstrap",
            "Success",
            "Đã lưu storage_state của StackShare để tái sử dụng cho các lần chạy sau."
        )

    async def bootstrap_connect(self, browser, timeout_ms: int = 180000):
        context = await browser.new_context(**self._base_context_args())
        page = await context.new_page()
        await self._apply_stealth(context, page)

        try:
            await self.handler.log_audit(
                "LoginCheck",
                "Running",
                "Đang mở trang chủ StackShare để bạn login lần đầu..."
            )
            await page.goto(
                STACKSHARE_LOGIN_URL,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            await self.handler.log_audit(
                "LoginCheck",
                "Running",
                "Please login to StackShare bằng GitHub hoặc Google. Hệ thống sẽ lưu storage_state sau khi chuyển sang dashboard."
            )

            await page.wait_for_url("**/dashboard", timeout=timeout_ms)

            await self._save_session(context)
            await self.handler.log_audit(
                "LoginCheck",
                "Success",
                "Đăng nhập StackShare thành công, session đã được lưu."
            )
            return context
        except Exception:
            await context.close()
            raise

    async def ensure_authenticated(self, browser):
        context_args = self._base_context_args()
        if not await self._materialize_storage_state_file():
            raise ValueError(
                "Chưa có storage_state của StackShare. Hãy tạo file session local rồi upload vào backend trước khi Submit."
            )
        context_args.update(self.session_store.context_kwargs())

        context = await browser.new_context(**context_args)
        page = await context.new_page()
        await self._apply_stealth(context, page)

        try:
            await self.handler.log_audit(
                "LoginCheck",
                "Running",
                "Đang truy cập StackShare và kiểm tra trạng thái Session đã lưu..."
            )
            try:
                await page.goto(STACKSHARE_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            except Exception:
                await page.goto(STACKSHARE_LOGIN_URL, wait_until="load", timeout=30000)

            await page.wait_for_timeout(1500)
            current_url = page.url
            login_form_visible = await self._has_visible_login_form(page)
            is_logged_out = login_form_visible

            await self.handler.log_audit(
                "LoginCheck",
                "Running",
                f"URL sau khi truy cập: {current_url}. Login form visible: {login_form_visible}."
            )

            if is_logged_out:
                err_msg = "Session StackShare hết hạn hoặc không hợp lệ. Hãy Connect Account lại."
                await self.handler.log_audit("LoginCheck", "Failed", err_msg)
                raise ValueError(err_msg)

            await self.handler.log_audit(
                "SessionBootstrap",
                "Success",
                "Đã load storage_state và xác thực session thành công."
            )
            return context
        except Exception:
            await context.close()
            raise
