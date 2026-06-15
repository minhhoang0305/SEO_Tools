from __future__ import annotations

import argparse
import asyncio
import os
import platform
from shutil import which
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường backend/seo-audit-worker đã cài requirements."
    ) from exc


FUTURETOOLS_URL = "https://futuretools.io/submit-a-tool"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1]
    / ".playwright"
    / "futuretools_storage_state.json"
)
DEFAULT_PROFILE_DIR = (
    Path(__file__).resolve().parents[1]
    / ".playwright"
    / "futuretools_chrome_profile"
)


def get_chrome_profile_path() -> tuple[str, str]:
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        user_data_dir = str(home / "AppData" / "Local" / "Google" / "Chrome" / "User Data")
    elif system == "Darwin":
        user_data_dir = str(home / "Library" / "Application Support" / "Google" / "Chrome")
    else:
        user_data_dir = str(home / ".config" / "google-chrome")

    playwright_user_data = str(Path(__file__).resolve().parent / ".chrome_profile_tmp_futuretools")
    return user_data_dir, playwright_user_data


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("FUTURETOOLS_CHROME_EXECUTABLE_PATH", "") or "").strip()
    if raw_value:
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
        if found:
            return found

    return None


async def connect_futuretools(output_path: Path, timeout_ms: int) -> None:
    async with async_playwright() as p:
        profile_dir = Path(os.getenv("FUTURETOOLS_PROFILE_DIR", DEFAULT_PROFILE_DIR))
        profile_dir.mkdir(parents=True, exist_ok=True)
        launch_kwargs = {
            "user_data_dir": str(profile_dir),
            "headless": False,
            "viewport": {"width": 1280, "height": 900},
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
            await page.goto(FUTURETOOLS_URL, wait_until="domcontentloaded", timeout=30000)
            print("Chrome thật đã mở FutureTools.")
            print("Hãy hoàn tất xác thực người thật nếu trang yêu cầu.")
            input("Sau khi verify xong, nhấn Enter để lưu session... ")

            output_path.parent.mkdir(parents=True, exist_ok=True)
            await context.storage_state(path=str(output_path))
            os.environ.setdefault("FUTURETOOLS_PROFILE_DIR", str(profile_dir))
            print(f"Session đã được lưu tại: {output_path}")
            print(f"Chrome profile đã dùng: {profile_dir}")
        finally:
            await context.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open FutureTools in real Chrome, let user verify, then save storage_state.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to save futuretools storage_state JSON.")
    parser.add_argument("--timeout-ms", type=int, default=300000, help="Unused placeholder for CLI symmetry.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.environ.setdefault("FUTURETOOLS_BROWSER_CHANNEL", "chrome")
    asyncio.run(connect_futuretools(args.output.expanduser(), args.timeout_ms))


if __name__ == "__main__":
    main()
