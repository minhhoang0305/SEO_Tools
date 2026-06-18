from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.async_api import async_playwright

from app.engines.submit_platforms.browser_platforms.kyi_ai.form_mapper import KYIAiFormMapper
from app.engines.submit_platforms.browser_platforms.kyi_ai.submit_handler import KYIAiSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper


async def main():
    os.environ["KYI_AI_DEBUG_HEADFUL"] = "1"
    os.environ["KYI_AI_DEBUG_SLOWMO_MS"] = "350"

    metadata = {
        "SiteName": "Kyi AI",
        "WebsiteUrl": "https://kyi.ai",
        "ContactEmail": "support@kyi.ai",
    }

    platform_info = {
        "PlatformCode": "kyi_ai",
        "JobDetailId": "debug-local",
    }

    handler = KYIAiSubmitHandler(platform_info=platform_info, db_repo=None)
    form_mapper = KYIAiFormMapper(handler)

    async with async_playwright() as p:
        launch_kwargs = {
            "headless": False,
            "slow_mo": 350,
            "args": ["--disable-blink-features=AutomationControlled"],
        }
        chrome_path = handler._chrome_executable_path()
        if chrome_path:
            launch_kwargs["executable_path"] = chrome_path
        else:
            launch_kwargs["channel"] = "chrome"

        browser = await p.chromium.launch(**launch_kwargs)
        browser_helper = BrowserAutomationHelper(browser)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        try:
            await page.goto("https://kyi.ai/submit", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1200)

            defaults = form_mapper.build_defaults(metadata, "https://kyi.ai")
            await form_mapper.fill_form(page, browser_helper, defaults)

            print("Filled Kyi AI form. Leave the browser open to inspect the values.")
            await asyncio.to_thread(input, "Press Enter here to close the browser...\n")
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
