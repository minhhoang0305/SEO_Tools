from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
from shutil import which

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy cài trong backend/seo-audit-worker trước khi chạy tool này."
    ) from exc


AWESOME_INDY_HOME_URL = "https://awesomeindie.com"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / ".playwright" / "awesome_indie_storage_state.json"
DEFAULT_PROFILE_DIR = Path(__file__).resolve().parents[1] / ".playwright" / "awesome_indie_chrome_profile"


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("AWESOME_INDIE_CHROME_EXECUTABLE_PATH", "") or "").strip()
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


async def _has_add_product_button(page) -> bool:
    selectors = [
        "button:has-text('AddProduct')",
        "button:has-text('Add Product')",
        "a:has-text('AddProduct')",
        "a:has-text('Add Product')",
    ]
    for selector in selectors:
        try:
            locator = page.locator(selector)
            if await locator.count() > 0 and await locator.first.is_visible():
                return True
        except Exception:
            continue
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Login Awesome Indie locally with Google OAuth and save Playwright storage_state.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to save awesome_indie storage_state JSON.")
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR, help="Chrome profile dir dùng cho Playwright.")
    parser.add_argument("--timeout-ms", type=int, default=300000, help="Timeout chờ user login xong.")
    return parser.parse_args()


async def connect_awesome_indie(output_path: Path, profile_dir: Path, timeout_ms: int) -> None:
    async with async_playwright() as p:
        profile_dir.mkdir(parents=True, exist_ok=True)
        launch_kwargs = {
            "user_data_dir": str(profile_dir),
            "headless": False,
            "viewport": {"width": 1440, "height": 1000},
            "args": ["--disable-blink-features=AutomationControlled"],
        }

        executable_path = get_chrome_executable_path()
        if executable_path:
            launch_kwargs["executable_path"] = executable_path
        else:
            launch_kwargs["channel"] = "chrome"

        context = await p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.pages[0] if context.pages else await context.new_page()

        try:
            await page.goto(AWESOME_INDY_HOME_URL, wait_until="domcontentloaded", timeout=30000)
            for selector in (
                "button:has-text('Continue with Google')",
                "button:has-text('Sign in with Google')",
                "button:has-text('Google')",
                "a:has-text('Continue with Google')",
                "a:has-text('Sign in with Google')",
            ):
                try:
                    locator = page.locator(selector)
                    if await locator.count() > 0 and await locator.first.is_visible():
                        await locator.first.click(no_wait_after=True, timeout=3000)
                        break
                except Exception:
                    continue

            print("Chrome thật đã mở Awesome Indie.")
            print("Hãy hoàn tất Google OAuth / đăng nhập nếu trang yêu cầu.")
            print("Khi đăng nhập xong và thấy AddProduct, nhấn Enter ở terminal để lưu session.")

            deadline = asyncio.get_running_loop().time() + (timeout_ms / 1000.0)
            while asyncio.get_running_loop().time() < deadline:
                if await _has_add_product_button(page):
                    break
                await page.wait_for_timeout(1000)

            input()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            await context.storage_state(path=str(output_path))
            print(f"Session đã được lưu tại: {output_path}")
            print(f"Chrome profile đã dùng: {profile_dir}")
        finally:
            await context.close()


def main() -> None:
    args = parse_args()
    asyncio.run(connect_awesome_indie(args.output.expanduser(), args.profile_dir.expanduser(), args.timeout_ms))


if __name__ == "__main__":
    main()
