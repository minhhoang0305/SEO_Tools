from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from shutil import which

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.engines.submit_platforms.browser_platforms.tenwords import TenWordsSubmitHandler

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường backend/seo-audit-worker đã cài requirements."
    ) from exc


LOGIN_URL = "https://portal.10words.io/auth/login"
SUBMISSIONS_URL = "https://portal.10words.io/submissions"
SUBMIT_URL = "https://portal.10words.io/submissions/submit"
DEFAULT_OUTPUT = PROJECT_ROOT / ".playwright" / "tenwords_storage_state.json"
DEFAULT_SCREENSHOT = PROJECT_ROOT / ".playwright" / "tenwords_submit.png"
DEFAULT_PROFILE_DIR = PROJECT_ROOT / ".playwright" / "tenwords_submit_profile"


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
    parser = argparse.ArgumentParser(description="Login 10words and automate submit in Chrome.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT)
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--step-by-step", action="store_true")
    parser.add_argument("--auto-submit", action="store_true")
    parser.add_argument("--api-token", default="", help="Token API của 10words. Nếu có token thì handler sẽ submit qua API.")
    parser.add_argument("--email", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--project-name", default="My Project")
    parser.add_argument("--description", default="A project worth checking out.")
    parser.add_argument("--project-url", default="https://example.com")
    parser.add_argument("--twitter-handle", default="")
    parser.add_argument("--category", default="Website", choices=["Mobile App", "Website", "SaaS", "Newsletter", "Other"])
    parser.add_argument("--newsletter", default="No thanks", choices=["Daily", "Daily (Mon-Thu)", "Weekly", "Weekly Digest", "No thanks"])
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


async def run() -> None:
    args = parse_args()
    if not args.api_token and (not args.email or not args.password):
        raise SystemExit("Hãy truyền --api-token hoặc cung cấp đủ --email và --password.")

    metadata = {
        "SiteName": args.project_name,
        "Description": args.description,
        "WebsiteUrl": args.project_url,
        "TwitterHandle": args.twitter_handle,
        "Category": args.category,
        "NewsletterOptIn": args.newsletter,
    }
    if args.api_token:
        metadata["TenWordsApiToken"] = args.api_token
        platform_info = {
            "PlatformCode": "tenwords",
            "JobDetailId": "00000000-0000-0000-0000-000000000000",
            "ApiToken": args.api_token,
        }
        handler = TenWordsSubmitHandler(platform_info, db_repo=None)
        result = await handler.submit(args.project_url, metadata, mode="final")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

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
            await _fill_first(page, ["input[type='email']", "input[name='email']"], args.email)
            _pause(args.step_by_step, "Đã điền email")
            await _fill_first(page, ["input[type='password']", "input[name='password']"], args.password)
            _pause(args.step_by_step, "Đã điền password")
            await _click_first(page, ["button[type='submit']", "button:has-text('Sign in')", "button:has-text('Login')"])
            await page.wait_for_timeout(2000)

            await page.goto(SUBMISSIONS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1000)
            await _click_first(page, ["button:has-text('Submit another Project')", "button:has-text('Submit Project')"])
            await page.wait_for_timeout(1000)
            if "submissions/submit" not in (page.url or ""):
                await page.goto(SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1000)

            await _fill_first(page, ["input[placeholder*='Enter the name of your project']", "input[name='projectName']", "input[name='name']"], args.project_name)
            _pause(args.step_by_step, "Đã điền Project Name")
            await _fill_first(page, ["textarea[placeholder*='Describe your project']", "textarea[name='description']", "textarea"], args.description)
            _pause(args.step_by_step, "Đã điền Description")
            await _fill_first(page, ["input[placeholder*='full link']", "input[name='projectUrl']", "input[type='url']", "input[type='text']"], args.project_url)
            _pause(args.step_by_step, "Đã điền Project URL")
            await _fill_first(page, ["input[placeholder*='Twitter']", "input[name='twitter']", "input[type='text']"], args.twitter_handle.lstrip("@"))
            _pause(args.step_by_step, "Đã điền Twitter Handle")

            category_map = {
                "Mobile App": "push-app",
                "Website": "push-website",
                "SaaS": "push-saas",
                "Newsletter": "push-newsletter",
                "Other": "push-other",
            }
            newsletter_map = {
                "Daily": "newsletter-daily",
                "Daily (Mon-Thu)": "newsletter-daily",
                "Weekly": "newsletter-weekly",
                "Weekly Digest": "newsletter-weekly",
                "No thanks": "newsletter-none",
            }
            try:
                await page.locator(f"input#{category_map[args.category]}").check()
            except Exception:
                pass
            _pause(args.step_by_step, "Đã chọn category")
            try:
                await page.locator(f"input#{newsletter_map[args.newsletter]}").check()
            except Exception:
                pass
            _pause(args.step_by_step, "Đã chọn newsletter")

            if args.auto_submit:
                await _click_first(page, ["button.btn-primary:has-text('Submit Project')", "button:has-text('Submit Project')", "button[type='button']"])
                await page.wait_for_timeout(1500)

            output_path = args.output.expanduser()
            screenshot_path = args.screenshot.expanduser()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=True)
            await context.storage_state(path=str(output_path))
            print(f"Screenshot: {screenshot_path}")
            print(f"Storage state: {output_path}")
        finally:
            await context.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
