from __future__ import annotations

import argparse
import asyncio
import os
import re
from pathlib import Path
from shutil import which

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường backend/seo-audit-worker đã cài requirements."
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://bai.tools/submit-ai-tools"
DEFAULT_OUTPUT = PROJECT_ROOT / ".playwright" / "baitools_submit_storage_state.json"
DEFAULT_SCREENSHOT = PROJECT_ROOT / ".playwright" / "baitools_submit.png"
DEFAULT_PROFILE_DIR = PROJECT_ROOT / ".playwright" / "baitools_submit_profile"


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("BAITOOLS_CHROME_EXECUTABLE_PATH", "") or "").strip()
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
    parser = argparse.ArgumentParser(description="Open BAI.tools submit form in Chrome and automate filling.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--no-open-form", action="store_true")
    parser.add_argument("--tool-name", default="")
    parser.add_argument("--website-url", default="")
    parser.add_argument("--step-by-step", action="store_true")
    parser.add_argument("--auto-submit", action="store_true")
    return parser.parse_args()


async def _click_first(page, selectors: list[str]) -> bool:
    for selector in selectors:
        locator = page.locator(selector)
        if await locator.count() == 0:
            continue
        try:
            target = locator.first
            await target.scroll_into_view_if_needed(timeout=2000)
            await target.click()
            return True
        except Exception:
            continue
    return False


async def _fill_first(page, selectors: list[str], value: str) -> bool:
    if not value:
        return False
    for selector in selectors:
        locator = page.locator(selector)
        if await locator.count() == 0:
            continue
        try:
            target = locator.first
            await target.scroll_into_view_if_needed(timeout=2000)
            await target.fill(value)
            return True
        except Exception:
            continue
    return False


def _pause(enabled: bool, message: str) -> None:
    if enabled:
        input(f"{message}\nNhấn Enter để tiếp tục... ")


async def submit_baitools(url: str, output_path: Path, screenshot_path: Path, profile_dir: Path, headless: bool, open_form: bool, step_by_step: bool, auto_submit: bool, tool_name: str, website_url: str) -> None:
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
            if open_form:
                await _click_first(page, [
                    "button:has-text('Submit your AI Tool')",
                    "button:has-text('Submit your AI tool')",
                    "text=Submit your AI Tool",
                ])
                await page.wait_for_timeout(1000)

            await _fill_first(page, [
                "input[placeholder*='name of your AI Tools']",
                "input[placeholder*='AI Tool Name']",
                "input[type='text']",
            ], tool_name)
            _pause(step_by_step, "Đã điền AI Tool Name")

            await _fill_first(page, [
                "input[placeholder*='website']",
                "input[placeholder*='URL']",
                "input[type='url']",
            ], website_url)
            _pause(step_by_step, "Đã điền Website URL")

            if auto_submit:
                submitted = await _click_first(page, [
                    "button[type='submit']",
                    "button:has-text('Submit')",
                    "input[type='submit']",
                ])
                if submitted:
                    await page.wait_for_timeout(1500)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=True)
            await context.storage_state(path=str(output_path))
            print(f"Screenshot: {screenshot_path}")
            print(f"Storage state: {output_path}")
        finally:
            await context.close()


def main() -> None:
    args = parse_args()
    asyncio.run(
        submit_baitools(
            args.url,
            args.output.expanduser(),
            args.screenshot.expanduser(),
            args.profile_dir.expanduser(),
            args.headless,
            not args.no_open_form,
            args.step_by_step,
            args.auto_submit,
            args.tool_name,
            args.website_url,
        )
    )


if __name__ == "__main__":
    main()
