from __future__ import annotations

import re
import time
from typing import Any, Dict

from playwright.async_api import async_playwright

from app.auth.strategies.productburst import ProductBurstAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.retry_timeout import RetryTimeoutHandler

from .constants import (
    PRODUCTBURST_BASE_URL,
    PRODUCTBURST_LAUNCHPAD_URL_PATTERN,
    PRODUCTBURST_PRE_LAUNCH_URL,
    PRODUCTBURST_SUCCESS_PATTERNS,
)
from .form_mapper import ProductBurstFormMapper
from .result_parser import ProductBurstResultParser
from .selectors import PRODUCTBURST_LAUNCH_BUTTON_SELECTORS


class ProductBurstSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = ProductBurstAuthStrategy

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.form_mapper = ProductBurstFormMapper(self)
        self.result_parser = ProductBurstResultParser()

    async def _wait_for_launchpad_url(self, page, timeout_ms: int = 15000) -> str:
        deadline = time.time() + (timeout_ms / 1000.0)
        while time.time() < deadline:
            current_url = page.url
            match = re.search(PRODUCTBURST_LAUNCHPAD_URL_PATTERN, current_url or "")
            if match:
                return current_url

            body_text = ""
            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
            except Exception:
                pass

            if any(pattern in body_text for pattern in PRODUCTBURST_SUCCESS_PATTERNS):
                return current_url

            await page.wait_for_timeout(500)

        return page.url

    def _resolve_launch_plan(self, metadata: Dict[str, Any]) -> str:
        return (metadata.get("LaunchPlan") or metadata.get("ProductType") or "Launch").strip()

    async def submit(self, url: str, metadata: Dict[str, Any], mode: str = "final") -> Dict[str, Any]:
        start_time = time.time()
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=20.0)

        await self.log_audit(
            "BrowserLaunch",
            "Running",
            "Đang khởi chạy Chromium để làm việc với ProductBurst..."
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            browser_helper = BrowserAutomationHelper(browser)
            self.form_mapper.bind_browser_helper(browser_helper)

            context = None
            try:
                context = await self.create_authenticated_context(browser)
                page = await context.new_page()

                await self.log_audit(
                    "NavigatePreLaunch",
                    "Running",
                    f"Đang điều hướng đến: {PRODUCTBURST_PRE_LAUNCH_URL}"
                )
                try:
                    await page.goto(PRODUCTBURST_PRE_LAUNCH_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(PRODUCTBURST_PRE_LAUNCH_URL, wait_until="load", timeout=30000)

                await page.wait_for_timeout(1000)

                defaults = self.form_mapper.build_defaults(metadata, url)
                extracted = await self.form_mapper.extract_form_data(page)
                collected = self.form_mapper.normalize_extracted_data(extracted, defaults)

                await self.log_audit(
                    "Page2Preview",
                    "Success",
                    self.result_parser.format_preview(collected)
                )

                if mode.lower() == "preview":
                    return {
                        "success": True,
                        "requires_manual_action": True,
                        "response_data": self.result_parser.build_preview_payload(collected),
                        "error_message": None,
                    }

                await self.log_audit(
                    "FillPage2",
                    "Running",
                    "Đang đổ dữ liệu page 2 vào ProductBurst..."
                )
                await self.form_mapper.fill_prelaunch_form(page, browser_helper, collected)

                selected_plan = self._resolve_launch_plan(metadata)
                if selected_plan:
                    await self.log_audit(
                        "ChoosePlan",
                        "Running",
                        f"Đang chọn gói launch: {selected_plan}"
                    )
                    await browser_helper.click_first_visible(
                        page,
                        [
                            f"button:has-text('{selected_plan}')",
                            f"div:has-text('{selected_plan}')",
                            f"label:has-text('{selected_plan}')",
                        ],
                    )

                await page.wait_for_timeout(1000)
                await retry_helper.run(
                    lambda: browser_helper.wait_for_button_enabled(
                        page,
                        "button",
                        "Launch",
                        timeout=15000,
                    )
                )

                if not await browser_helper.click_first_visible(page, PRODUCTBURST_LAUNCH_BUTTON_SELECTORS):
                    raise ValueError("Không tìm thấy nút Launch trên ProductBurst.")

                await self.log_audit(
                    "Launch",
                    "Running",
                    "Đã bấm Launch. Đang chờ ProductBurst tạo launchpad URL..."
                )

                await page.wait_for_timeout(1000)
                final_url = await self._wait_for_launchpad_url(page, timeout_ms=20000)
                launchpad_id = self.form_mapper.extract_launchpad_id(final_url)

                if not launchpad_id:
                    launchpad_id = (metadata.get("LaunchpadId") or "").strip()

                if not final_url or PRODUCTBURST_BASE_URL not in final_url:
                    err_msg = "ProductBurst chưa trả về launchpad URL hợp lệ."
                    await self.log_audit("Launch", "Failed", err_msg)
                    return {
                        "success": False,
                        "response_data": self.result_parser.build_pending_payload(err_msg),
                        "error_message": err_msg,
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit(
                    "Launch",
                    "Success",
                    f"ProductBurst trả về launchpad URL: {final_url}. Thời gian: {duration}ms",
                    duration,
                )

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(
                        collected,
                        launchpad_url=final_url,
                        launchpad_id=launchpad_id,
                        selected_plan=selected_plan,
                    ),
                    "error_message": None,
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi thao tác ProductBurst: {str(e)}"
                await self.log_audit("Launch", "Failed", err_msg, duration)
                return {
                    "success": False,
                    "response_data": None,
                    "error_message": err_msg,
                }
            finally:
                if context is not None:
                    await context.close()
                await browser.close()

