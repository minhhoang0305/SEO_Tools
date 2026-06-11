from __future__ import annotations

import time
from typing import Dict, Any

from playwright.async_api import async_playwright

from app.auth.strategies.stackshare import StackShareAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import BaseBrowserSubmitHandler
from app.platforms.browser_automation import BrowserAutomationHelper
from app.platforms.retry_timeout import RetryTimeoutHandler

from .constants import (
    STACKSHARE_CONTINUE_SELECTORS,
    STACKSHARE_CONTINUE_SELECTOR,
    STACKSHARE_LIST_TOOL_SELECTORS,
    STACKSHARE_LIST_TOOL_SELECTOR,
    STACKSHARE_SUBMISSION_SUCCESS_PATTERNS,
    STACKSHARE_SUBMIT_SELECTORS,
    STACKSHARE_SUBMIT_SELECTOR,
    STACKSHARE_SUBMIT_URL,
)
from .cooldown_detector import StackShareCooldownDetector
from .form_mapper import StackShareFormMapper
from .logo_uploader import StackShareLogoUploader
from .result_parser import StackShareResultParser


class StackShareSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = StackShareAuthStrategy

    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        super().__init__(platform_info, db_repo)
        self.cooldown_detector = StackShareCooldownDetector()
        self.form_mapper = StackShareFormMapper(self)
        self.logo_uploader = StackShareLogoUploader(self)
        self.result_parser = StackShareResultParser()

    async def _wait_for_submission_confirmation(self, page, timeout_ms: int = 12000):
        deadline = time.time() + (timeout_ms / 1000.0)

        while time.time() < deadline:
            try:
                body_text = (await page.locator("body").inner_text(timeout=2000)).strip().lower()
            except Exception:
                body_text = ""

            for pattern in STACKSHARE_SUBMISSION_SUCCESS_PATTERNS:
                if pattern in body_text:
                    return {
                        "source": "body",
                        "matched_text": pattern,
                    }

            await page.wait_for_timeout(500)

        return None

    async def submit(self, url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=15.0)

        await self.log_audit(
            "BrowserLaunch",
            "Running",
            "Đang khởi chạy trình duyệt Chromium (Playwright)..."
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            browser_helper = BrowserAutomationHelper(browser)
            self.form_mapper.bind_browser_helper(browser_helper)

            context = None
            try:
                context = await self.create_authenticated_context(browser)
                page = await context.new_page()

                await self.log_audit(
                    "NavigateSubmit",
                    "Running",
                    f"Đang điều hướng đến: {STACKSHARE_SUBMIT_URL}"
                )
                try:
                    await page.goto(STACKSHARE_SUBMIT_URL, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    await page.goto(STACKSHARE_SUBMIT_URL, wait_until="load", timeout=30000)
                await page.wait_for_timeout(1000)

                await self.log_audit(
                    "OpenListTool",
                    "Running",
                    "Đang mở luồng List a Tool của StackShare..."
                )
                await browser_helper.click_first_visible(
                    page,
                    STACKSHARE_LIST_TOOL_SELECTORS + [STACKSHARE_LIST_TOOL_SELECTOR]
                )

                await page.wait_for_timeout(1000)

                logo_file_path = self.logo_uploader.resolve_logo_file_path(metadata)
                defaults = self.form_mapper.build_defaults(metadata, url, logo_file_path)

                await self.log_audit(
                    "FillUrl",
                    "Running",
                    "Đang nhập Website URL và cho StackShare crawl dữ liệu..."
                )
                url_filled = await self.form_mapper.fill_url(page, url, browser_helper)
                if not url_filled:
                    raise ValueError("Không tìm thấy field nhập Website URL trên StackShare.")

                await page.locator("#website-url").blur()
                await page.wait_for_timeout(500)
                await retry_helper.run(
                    lambda: browser_helper.wait_for_button_enabled(page, "button", "Continue", timeout=15000)
                )

                if not await browser_helper.click_first_visible(
                    page,
                    STACKSHARE_CONTINUE_SELECTORS + [STACKSHARE_CONTINUE_SELECTOR]
                ):
                    raise ValueError("Không tìm thấy nút Continue trên StackShare.")

                await self.log_audit(
                    "WaitCrawl",
                    "Running",
                    "Đang chờ StackShare crawl website và hiển thị form chi tiết..."
                )

                await page.wait_for_timeout(1000)
                cooldown_hint = await self.cooldown_detector.wait_for_crawl_or_cooldown(page, timeout_ms=5000)
                if cooldown_hint:
                    remaining_hours = cooldown_hint.get("remaining_hours") or ""
                    remaining_text = f" Còn lại khoảng {remaining_hours} giờ." if remaining_hours else ""
                    err_msg = (
                        "StackShare đang chặn submit mới trong 24 giờ. "
                        f"Hãy đợi hết cooldown rồi thử lại.{remaining_text}"
                    )
                    await self.log_audit(
                        "CooldownCheck",
                        "Failed",
                        (
                            "Phát hiện trạng thái cooldown trên StackShare "
                            f"(nguồn: {cooldown_hint.get('source')}, khớp: {cooldown_hint.get('matched_text')}). "
                            f"{err_msg}"
                        )
                    )
                    return {
                        "success": False,
                        "response_data": None,
                        "error_message": err_msg
                    }

                crawled_raw = await self.form_mapper.extract_crawled_data(page)
                crawled = self.form_mapper.normalize_crawled_data(crawled_raw, defaults)

                await self.log_audit(
                    "CrawlPreview",
                    "Success",
                    self.result_parser.format_crawl_preview(crawled)
                )

                await self.log_audit(
                    "FillForm",
                    "Running",
                    "Đang đồng bộ dữ liệu crawl vào form trước khi submit..."
                )
                await self.form_mapper.apply_form(page, browser_helper, crawled)

                uploaded_logo = await self.logo_uploader.upload(page, metadata)
                if uploaded_logo:
                    crawled["logo"] = uploaded_logo

                await self.log_audit(
                    "UserReview",
                    "Running",
                    "Đã đồng bộ dữ liệu crawl. Nếu cần chỉnh sửa thêm, đây là bước review trước khi submit."
                )

                await page.wait_for_timeout(1000)
                cooldown_hint = await self.cooldown_detector.detect(page)
                if cooldown_hint:
                    remaining_hours = cooldown_hint.get("remaining_hours") or ""
                    remaining_text = f" Còn lại khoảng {remaining_hours} giờ." if remaining_hours else ""
                    err_msg = (
                        "StackShare đang chặn submit mới trong 24 giờ. "
                        f"Hãy đợi hết cooldown rồi thử lại.{remaining_text}"
                    )
                    await self.log_audit(
                        "CooldownCheck",
                        "Failed",
                        (
                            "Phát hiện trạng thái cooldown trên StackShare "
                            f"(nguồn: {cooldown_hint.get('source')}, khớp: {cooldown_hint.get('matched_text')}). "
                            f"{err_msg}"
                        )
                    )
                    return {
                        "success": False,
                        "response_data": None,
                        "error_message": err_msg
                    }

                await retry_helper.run(
                    lambda: browser_helper.wait_for_button_enabled(page, "[role='dialog'] button", "Submit", timeout=15000)
                )

                if not await browser_helper.click_first_visible(page, STACKSHARE_SUBMIT_SELECTORS + [STACKSHARE_SUBMIT_SELECTOR]):
                    raise ValueError("Không tìm thấy nút Submit trên StackShare.")

                await self.log_audit(
                    "Submit",
                    "Running",
                    "Đã bấm Submit. Đang chờ StackShare xác nhận kết quả thực tế..."
                )

                submission_confirmation = await self._wait_for_submission_confirmation(page, timeout_ms=12000)
                if not submission_confirmation:
                    err_msg = (
                        "Đã bấm Submit nhưng chưa nhận được xác nhận thành công từ StackShare. "
                        "Không thể coi là submit thành công."
                    )
                    await self.log_audit(
                        "Submit",
                        "Failed",
                        err_msg
                    )
                    return {
                        "success": False,
                        "response_data": None,
                        "error_message": err_msg
                    }

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit(
                    "Submit",
                    "Success",
                    (
                        "Đã nhận được xác nhận submit thành công từ StackShare "
                        f"(nguồn: {submission_confirmation.get('source')}, khớp: {submission_confirmation.get('matched_text')}). "
                        f"Thời gian: {duration}ms"
                    ),
                    duration
                )

                return {
                    "success": True,
                    "response_data": self.result_parser.build_success_payload(crawled.get("tool_name", ""), crawled),
                    "error_message": None
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi trong quá trình thao tác giao diện tự động trên StackShare: {str(e)}"
                await self.log_audit("NavigateSubmit", "Failed", err_msg, duration)
                return {
                    "success": False,
                    "response_data": None,
                    "error_message": err_msg
                }
            finally:
                if context is not None:
                    await context.close()
                await browser.close()
