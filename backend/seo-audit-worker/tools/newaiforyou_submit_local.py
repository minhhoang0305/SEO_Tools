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

from app.engines.submit_platforms.browser_platforms.newaiforyou.form_mapper import NewAIForYouFormMapper
from app.engines.submit_platforms.browser_platforms.newaiforyou.submit_handler import NewAIForYouSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper
from app.session.storage_state_store import FileStorageStateStore


NEWAIFORYOU_HOME_URL = "https://newaiforyou.com"
NEWAIFORYOU_SUBMIT_URL = "https://newaiforyou.com/submit"
DEFAULT_STORAGE_STATE = Path(__file__).resolve().parents[1] / ".playwright" / "newaiforyou_storage_state.json"


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("NEWAIFORYOU_CHROME_EXECUTABLE_PATH", "") or "").strip()
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
    parser = argparse.ArgumentParser(description="Open New AI For You in real Chrome and submit a sample tool.")
    parser.add_argument("--storage-state", type=Path, default=DEFAULT_STORAGE_STATE, help="Path storage_state JSON của New AI For You.")
    parser.add_argument("--headful", action="store_true", help="Giữ browser headful để theo dõi thao tác.")
    return parser.parse_args()


async def main_async(storage_state: Path, headful: bool) -> None:
    if not storage_state.exists():
        raise SystemExit(
            f"Chưa thấy storage_state tại {storage_state}. Hãy chạy newaiforyou_connect_local.py trước."
        )

    async with async_playwright() as p:
        launch_kwargs = {
            "headless": not headful,
            "args": ["--disable-blink-features=AutomationControlled"],
        }
        executable_path = get_chrome_executable_path()
        if executable_path:
            launch_kwargs["executable_path"] = executable_path
        else:
            launch_kwargs["channel"] = "chrome"

        browser = await p.chromium.launch(**launch_kwargs)
        browser_helper = BrowserAutomationHelper(browser)
        handler = NewAIForYouSubmitHandler({"PlatformCode": "newaiforyou"}, db_repo=None)
        handler.form_mapper = NewAIForYouFormMapper(handler)

        context = await browser.new_context(**FileStorageStateStore(str(storage_state)).context_kwargs())
        page = await context.new_page()

        try:
            await page.goto(NEWAIFORYOU_HOME_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1000)
            if not await handler.form_mapper.click_add_product(page, browser_helper):
                await page.goto(NEWAIFORYOU_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
            else:
                await page.wait_for_timeout(1200)

            if "/submit" not in (page.url or ""):
                await page.goto(NEWAIFORYOU_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1200)

            defaults = {
                "tool_name": "Langflow",
                "url": "https://www.langflow.org",
            }

            await handler.form_mapper.fill_form(page, browser_helper, defaults)
            await page.wait_for_timeout(500)
            await handler.form_mapper.click_submit(page, browser_helper)
            print("Đã điền và bấm Submit trên New AI For You.")
            await page.wait_for_timeout(8000)
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main_async(args.storage_state.expanduser(), args.headful))
