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
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường backend/seo-audit-worker đã cài requirements."
    ) from exc


LOGIN_URL = "https://portal.10words.io/auth/login"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / ".playwright" / "tenwords_storage_state.json"
DEFAULT_PROFILE_DIR = Path(__file__).resolve().parents[1] / ".playwright" / "tenwords_chrome_profile"


def get_chrome_executable_path() -> str | None:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open 10words login page in Chrome and save storage_state after manual login.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--headless", action="store_true")
    return parser.parse_args()


async def main_async() -> None:
    args = parse_args()
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
            await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            print("Chrome thật đã mở 10words login.")
            print("Hãy login bằng email/password trong browser.")
            input("Khi login xong, nhấn Enter để lưu session... ")

            output_path = args.output.expanduser()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            await context.storage_state(path=str(output_path))
            print(f"Session đã được lưu tại: {output_path}")
        finally:
            await context.close()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
