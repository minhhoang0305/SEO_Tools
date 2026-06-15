import argparse
import asyncio
import os
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy cài trong backend/seo-audit-worker trước khi chạy tool này."
    ) from exc


PRODUCTBURST_AUTH_URL = "https://productburst.com/"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1]
    / ".playwright"
    / "productburst_storage_state.json"
)


async def wait_for_url_contains(page, fragments: tuple[str, ...], timeout_ms: int) -> str:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + (timeout_ms / 1000.0)
    while loop.time() < deadline:
        current_url = page.url
        if any(fragment in current_url for fragment in fragments):
            return current_url
        await page.wait_for_timeout(500)

    raise TimeoutError(f"Không chờ thấy URL chứa một trong các đoạn: {fragments}")


async def wait_for_authenticated_state(page, timeout_ms: int) -> str:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + (timeout_ms / 1000.0)
    selectors = [
        "text=MY DASHBOARD",
        "text=Logout",
        "button:has-text('Submit Product')",
        "a:has-text('Submit Product')",
        "button:has-text('Launch your SaaS')",
        "a:has-text('Launch your SaaS')",
    ]

    while loop.time() < deadline:
        current_url = page.url
        if "/auth" not in current_url and "/signin" not in current_url and "/login" not in current_url:
            for selector in selectors:
                try:
                    locator = page.locator(selector)
                    if await locator.count() > 0 and await locator.first.is_visible():
                        return current_url
                except Exception:
                    continue

        await page.wait_for_timeout(500)

    raise TimeoutError("Không xác nhận được trạng thái đăng nhập của ProductBurst.")


async def connect_productburst(output_path: Path, method: str, email: str | None, password: str | None, timeout_ms: int) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            await page.goto(PRODUCTBURST_AUTH_URL, wait_until="domcontentloaded", timeout=30000)

            if method == "password":
                if not email or not password:
                    raise ValueError("Cần --email và --password khi dùng method=password.")

                await page.locator("input[type='email'], input[name='email']").first.fill(email)
                await page.locator("input[type='password'], input[name='password']").first.fill(password)
                await page.locator("button:has-text('Sign in'), button:has-text('Login'), button[type='submit']").first.click(
                    no_wait_after=True
                )
            else:
                google_login = page.locator(
                    "button:has-text('Continue with Google'), button:has-text('Google'), a:has-text('Continue with Google')"
                ).first
                try:
                    await google_login.click(no_wait_after=True, timeout=10000)
                except Exception:
                    # Google auth flow often keeps navigating through consent pages.
                    # The post-click URL wait below handles the actual landing page.
                    pass

            await page.wait_for_timeout(2000)
            await wait_for_url_contains(page, ("/pre-launch", "/launchpad/", "accounts.google", "/dashboard"), timeout_ms)

            if "accounts.google" in page.url:
                print("Google OAuth đã mở. Hoàn tất đăng nhập trong browser, sau đó chờ redirect về ProductBurst.")
                await wait_for_url_contains(page, ("/pre-launch", "/launchpad/"), timeout_ms)

            await wait_for_authenticated_state(page, timeout_ms)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            await context.storage_state(path=str(output_path))
            print(f"Connected. Session đã được lưu tại: {output_path}")
        finally:
            await context.close()
            await browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Login ProductBurst locally and save Playwright storage_state.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to save productburst storage_state JSON.")
    parser.add_argument("--method", choices=["google", "password"], default="password", help="Login method to use.")
    parser.add_argument("--email", type=str, default=os.getenv("PRODUCTBURST_EMAIL"), help="Email dùng cho method=password.")
    parser.add_argument("--password", type=str, default=os.getenv("PRODUCTBURST_PASSWORD"), help="Password dùng cho method=password.")
    parser.add_argument("--timeout-ms", type=int, default=300000, help="Timeout to wait for redirect after login.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(connect_productburst(args.output.expanduser(), args.method, args.email, args.password, args.timeout_ms))


if __name__ == "__main__":
    main()
