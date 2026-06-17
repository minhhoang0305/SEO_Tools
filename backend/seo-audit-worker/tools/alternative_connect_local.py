from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from shutil import which

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit("Thiếu dependency 'playwright'. Hãy cài trong backend/seo-audit-worker trước khi chạy tool này.") from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / ".playwright" / "alternative_storage_state.json"
DEFAULT_LOGIN_URL = os.getenv("ALTERNATIVE_LOGIN_URL", "https://alternative.me/account/submissions")


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("ALTERNATIVE_CHROME_EXECUTABLE_PATH", "") or "").strip()
    if raw_value and Path(raw_value).expanduser().exists():
        return raw_value
    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    for binary in ("google-chrome", "google-chrome-stable", "chrome", "chromium", "chromium-browser"):
        found = which(binary)
        if found and Path(found).exists():
            return found
    return None


async def connect_alternative(output_path: Path, username: str | None, password: str | None, timeout_ms: int) -> None:
    async with async_playwright() as p:
        launch_kwargs = {
            "headless": False,
            "args": ["--disable-blink-features=AutomationControlled"],
        }
        chrome_path = get_chrome_executable_path()
        if chrome_path:
            launch_kwargs["executable_path"] = chrome_path
        else:
            launch_kwargs["channel"] = "chrome"

        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            await page.goto(DEFAULT_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            print("Chrome thật đã mở Alternative.")

            if username and password:
                try:
                    await page.locator("input[type='email'], input[name='email'], input[name='username'], input[type='text']").first.fill(username)
                    await page.locator("input[type='password'], input[name='password']").first.fill(password)
                    await page.locator("button[type='submit'], button:has-text('Login'), button:has-text('Sign in'), button:has-text('Submit')").first.click(no_wait_after=True)
                except Exception:
                    print("Không tự fill được login form, bạn có thể login thủ công trong browser.")

            print("Hãy login xong trong browser rồi quay lại terminal.")
            input("Nhấn Enter để lưu session Alternative... ")

            output_path.parent.mkdir(parents=True, exist_ok=True)
            await context.storage_state(path=str(output_path))
            print(f"Session đã được lưu tại: {output_path}")
        finally:
            await context.close()
            await browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Login Alternative locally and save storage_state.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--username", default=os.getenv("ALTERNATIVE_USERNAME"))
    parser.add_argument("--password", default=os.getenv("ALTERNATIVE_PASSWORD"))
    parser.add_argument("--timeout-ms", type=int, default=300000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.environ.setdefault("ALTERNATIVE_DEBUG_HEADFUL", "1")
    asyncio.run(connect_alternative(args.output.expanduser(), args.username, args.password, args.timeout_ms))


if __name__ == "__main__":
    main()
