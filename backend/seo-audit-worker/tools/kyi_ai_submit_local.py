from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from shutil import which

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường backend/seo-audit-worker đã cài requirements."
    ) from exc

from app.engines.submit_platforms.browser_platforms.kyi_ai import KYIAiSubmitHandler
from app.engines.submit_platforms.browser_platforms.kyi_ai.form_mapper import KYIAiFormMapper

DEFAULT_URL = "https://kyi.ai/submit"
DEFAULT_OUTPUT = PROJECT_ROOT / ".playwright" / "kyi_ai_submit_storage_state.json"
DEFAULT_SCREENSHOT = PROJECT_ROOT / ".playwright" / "kyi_ai_submit.png"
DEFAULT_PROFILE_DIR = PROJECT_ROOT / ".playwright" / "kyi_ai_submit_profile"


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("KYI_AI_CHROME_EXECUTABLE_PATH", "") or "").strip()
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open Kyi AI submit form in Chrome and fill sample data.")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL sẽ mở.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path lưu storage_state JSON.")
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT, help="Path lưu screenshot PNG.")
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR, help="Chrome profile dir dùng cho Playwright.")
    parser.add_argument("--headless", action="store_true", help="Chạy ẩn browser.")
    parser.add_argument("--auto-submit", action="store_true", help="Tự bấm Submit sau khi điền xong.")
    parser.add_argument("--website-name", default="Kyi AI", help="Website Name.")
    parser.add_argument("--website-url", default="https://kyi.ai", help="Website URL.")
    parser.add_argument("--email", default="support@kyi.ai", help="Email.")
    return parser.parse_args()


async def run() -> None:
    args = parse_args()
    metadata = {
        "SiteName": args.website_name,
        "WebsiteUrl": args.website_url,
        "ContactEmail": args.email,
    }

    platform_info = {
        "PlatformCode": "kyi_ai",
        "JobDetailId": "00000000-0000-0000-0000-000000000000",
    }

    handler = KYIAiSubmitHandler(platform_info=platform_info, db_repo=None)
    form_mapper = KYIAiFormMapper(handler)

    async with async_playwright() as p:
        profile_dir = args.profile_dir.expanduser()
        profile_dir.mkdir(parents=True, exist_ok=True)
        launch_kwargs = {
            "user_data_dir": str(profile_dir),
            "headless": args.headless,
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
            await page.goto(args.url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1200)

            defaults = form_mapper.build_defaults(metadata, args.website_url)
            await form_mapper.fill_form(page, None, defaults)

            screenshot_path = args.screenshot.expanduser()
            output_path = args.output.expanduser()
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=True)
            await context.storage_state(path=str(output_path))

            print(f"Đã fill xong form Kyi AI.")
            print(f"Screenshot: {screenshot_path}")
            print(f"Storage state: {output_path}")

            if args.auto_submit:
                submit_button = page.get_by_role("button", name="Submit")
                if await submit_button.count() == 0:
                    print("Không tìm thấy nút Submit để auto-submit.")
                else:
                    await submit_button.first.click()
                    deadline = time.time() + 15
                    while time.time() < deadline:
                        try:
                            toast = page.locator("li[data-sonner-toast][data-type='success'], [data-sonner-toast][data-type='success']")
                            if await toast.count() > 0 and await toast.first.is_visible():
                                print("Đã thấy toast success từ Sonner.")
                                break
                        except Exception:
                            pass
                        await page.wait_for_timeout(500)
                    await page.wait_for_timeout(1500)
                    print(f"Đã auto-submit, current url: {page.url}")
            else:
                input("Nhấn Enter để đóng browser...")
        finally:
            await context.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
