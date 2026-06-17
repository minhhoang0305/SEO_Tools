from __future__ import annotations

import argparse
import asyncio
import os
import platform
import sys
from pathlib import Path
from shutil import which

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường backend/seo-audit-worker đã cài requirements."
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://spiff.store/"
DEFAULT_OUTPUT = PROJECT_ROOT / ".playwright" / "spiffstore_storage_state.json"
DEFAULT_SCREENSHOT = PROJECT_ROOT / ".playwright" / "spiffstore-manual.png"
DEFAULT_PROFILE_DIR = PROJECT_ROOT / ".playwright" / "spiffstore_chrome_profile"


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("SPIFFSTORE_CHROME_EXECUTABLE_PATH", "") or "").strip()
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
    parser = argparse.ArgumentParser(
        description="Open Spiff Store in real Chrome, let user interact manually, then save screenshot/storage_state."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="URL sẽ mở trong browser.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path lưu storage_state JSON.")
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT, help="Path lưu screenshot PNG.")
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR, help="Chrome profile dir dùng cho Playwright.")
    parser.add_argument("--headless", action="store_true", help="Chạy ẩn browser.")
    return parser.parse_args()


async def open_spiffstore(url: str, output_path: Path, screenshot_path: Path, profile_dir: Path, headless: bool) -> None:
    async with async_playwright() as p:
        profile_dir.mkdir(parents=True, exist_ok=True)
        launch_kwargs = {
            "user_data_dir": str(profile_dir),
            "headless": headless,
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
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            print(f"Đã mở: {url}")
            print("Bạn có thể tự thao tác trong browser.")
            print("Khi xong, quay lại terminal và nhấn Enter để chụp screenshot + lưu session.")
            input()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=True)
            await context.storage_state(path=str(output_path))

            print(f"Đã lưu screenshot: {screenshot_path}")
            print(f"Đã lưu storage_state: {output_path}")
            print(f"Chrome profile: {profile_dir}")
        finally:
            await context.close()


def main() -> None:
    args = parse_args()
    asyncio.run(
        open_spiffstore(
            args.url,
            args.output.expanduser(),
            args.screenshot.expanduser(),
            args.profile_dir.expanduser(),
            args.headless,
        )
    )


if __name__ == "__main__":
    main()
