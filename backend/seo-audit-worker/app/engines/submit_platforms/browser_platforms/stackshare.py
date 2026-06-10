import json
import os
import time
from pathlib import Path
from typing import Dict, Any

from playwright.async_api import async_playwright

from app.auth.strategies.stackshare import StackShareAuthStrategy
from app.engines.submit_platforms.browser_platforms.base_browser_handler import (
    BaseBrowserSubmitHandler
)


STACKSHARE_SUBMIT_URL = "https://stackshare.io/"
STACKSHARE_LIST_TOOL_SELECTOR = "a:has-text('List a Tool'), button:has-text('List a Tool')"
STACKSHARE_CONTINUE_SELECTOR = "button:has-text('Continue')"
STACKSHARE_SUBMIT_SELECTOR = "[role='dialog'] button:has-text('Submit')"
STACKSHARE_DEFAULT_SENTINELS = {
    "your",
    "your-site.com website hosting",
    "https://your-site.com/",
}


class StackShareSubmitHandler(BaseBrowserSubmitHandler):
    auth_strategy_cls = StackShareAuthStrategy

    async def _fill_first_visible(self, page, selectors, value: str) -> bool:
        if not value:
            return False

        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue    

            target = locator.first
            try:
                if await target.is_visible():
                    await target.fill(value)
                    return True
            except Exception:
                continue

        return False

    async def _read_first_visible(self, page, selectors) -> str:
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue

            target = locator.first
            try:
                if await target.is_visible():
                    tag_name = await target.evaluate("(el) => el.tagName.toLowerCase()")
                    if tag_name in ["input", "textarea"]:
                        return (await target.input_value()).strip()
                    return (await target.text_content() or "").strip()
            except Exception:
                continue

        return ""

    def _is_crawled_value_valid(self, value: str) -> bool:
        normalized = (value or "").strip().lower()
        if not normalized:
            return False
        return normalized not in STACKSHARE_DEFAULT_SENTINELS

    async def _wait_for_continue_enabled(self, page) -> None:
        await page.wait_for_function(
            """() => {
                const btn = Array.from(document.querySelectorAll('button'))
                    .find(el => (el.textContent || '').includes('Continue'));
                return btn && !btn.disabled;
            }"""
        )

    async def _wait_for_submit_enabled(self, page) -> None:
        await page.wait_for_function(
            """() => {
                const btn = Array.from(document.querySelectorAll("[role='dialog'] button"))
                    .find(el => (el.textContent || '').includes('Submit'));
                return btn && !btn.disabled;
            }"""
        )

    async def _click_first_visible(self, page, selectors) -> bool:
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue

            target = locator.first
            try:
                if await target.is_visible():
                    await target.click()
                    return True
            except Exception:
                continue

        return False

    def _resolve_logo_file_path(self, metadata: Dict[str, Any]) -> str:
        candidate_keys = [
            "LogoPath",
            "LogoFilePath",
            "LogoFile",
            "LogoLocalPath",
        ]

        for key in candidate_keys:
            value = (metadata.get(key) or "").strip()
            if value and Path(value).expanduser().exists():
                return str(Path(value).expanduser())

        logo_url = (metadata.get("LogoUrl") or metadata.get("Logo") or "").strip()
        if logo_url and Path(logo_url).expanduser().exists():
            return str(Path(logo_url).expanduser())

        return ""

    async def _upload_logo_file(self, page, metadata: Dict[str, Any]) -> str:
        logo_file_path = self._resolve_logo_file_path(metadata)
        if not logo_file_path:
            logo_url = (metadata.get("LogoUrl") or metadata.get("Logo") or "").strip()
            if logo_url:
                await self.log_audit(
                    "LogoUpload",
                    "Running",
                    "Logo được cung cấp dưới dạng URL, nhưng StackShare cần file local để upload. Bỏ qua logo."
                )
            return ""

        file_input_locator = page.locator("input[type='file'][accept*='image'], input[type='file']")
        if await file_input_locator.count() == 0:
            raise ValueError("Không tìm thấy input upload logo trên StackShare.")

        await file_input_locator.first.set_input_files(logo_file_path)
        await page.wait_for_timeout(1000)

        await self.log_audit(
            "LogoUpload",
            "Success",
            f"Đã upload logo từ file local: {os.path.basename(logo_file_path)}"
        )
        return logo_file_path

    async def submit(self, url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()

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

            context = None
            try:
                context = await self.create_authenticated_context(browser)
                page = await context.new_page()

                submit_page_url = STACKSHARE_SUBMIT_URL
                await self.log_audit(
                    "NavigateSubmit",
                    "Running",
                    f"Đang điều hướng đến: {submit_page_url}"
                )
                await page.goto(submit_page_url, wait_until="networkidle", timeout=30000)

                await self.log_audit(
                    "OpenListTool",
                    "Running",
                    "Đang mở luồng List a Tool của StackShare..."
                )
                await self._click_first_visible(
                    page,
                    [
                        STACKSHARE_LIST_TOOL_SELECTOR,
                        "a[href*='tool']",
                        "a[href*='submit']",
                        "a:has-text('Tool')"
                    ]
                )

                await page.wait_for_load_state("networkidle")

                site_name = metadata.get("SiteName") or "My SEO Tool Site"
                site_description = (
                    metadata.get("Description")
                    or "A premium online platform for SEO utilities and tracking."
                )
                site_short_description = (
                    metadata.get("ShortDescription")
                    or site_description
                )
                docs_url = metadata.get("DocsUrl") or metadata.get("DocumentationUrl") or ""
                features = metadata.get("Features") or metadata.get("Keywords") or ""
                logo_file_path = self._resolve_logo_file_path(metadata)

                await self.log_audit(
                    "FillUrl",
                    "Running",
                    "Đang nhập Website URL và cho StackShare crawl dữ liệu..."
                )
                url_filled = await self._fill_first_visible(
                    page,
                    [
                        "#website-url",
                        "input#website-url",
                        "input[type='url']"
                    ],
                    url
                )

                if not url_filled:
                    raise ValueError("Không tìm thấy field nhập Website URL trên StackShare.")

                await page.locator("#website-url").blur()
                await page.wait_for_timeout(500)
                await self._wait_for_continue_enabled(page)

                if not await self._click_first_visible(
                    page,
                    [
                        STACKSHARE_CONTINUE_SELECTOR,
                        "button:has-text('Continue')",
                        "button[type='submit']"
                    ]
                ):
                    raise ValueError("Không tìm thấy nút Continue trên StackShare.")

                await self.log_audit(
                    "WaitCrawl",
                    "Running",
                    "Đang chờ StackShare crawl website và hiển thị form chi tiết..."
                )

                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(3000)

                crawled_tool_name = await self._read_first_visible(
                    page,
                    [
                        "input[placeholder*='Tool Name']",
                        "input[name='name']",
                        "input[id='tool_name']",
                        "input[aria-label*='Name']",
                    ]
                )
                crawled_website_url = await self._read_first_visible(
                    page,
                    [
                        "input[placeholder*='Website URL']",
                        "input[type='url']",
                        "input[name='website']",
                        "input[name='url']",
                        "#website-url",
                    ]
                )
                crawled_docs_url = await self._read_first_visible(
                    page,
                    [
                        "input[placeholder*='Docs URL']",
                        "input[placeholder*='Documentation']",
                        "input[name='docs']",
                        "input[name='documentation']",
                    ]
                )
                crawled_description = await self._read_first_visible(
                    page,
                    [
                        "input[placeholder*='One-line description']",
                        "input[placeholder*='Short description']",
                        "textarea[placeholder='Short description (2-3 sentences) *']",
                        "textarea[placeholder*='Short description']",
                        "textarea[placeholder*='description']",
                        "textarea[aria-label*='Description']",
                    ]
                )
                crawled_short_description = await self._read_first_visible(
                    page,
                    [
                        "textarea[placeholder='Short description (2-3 sentences) *']",
                        "textarea[placeholder*='Short description']",
                        "textarea[placeholder*='description']",
                        "textarea[aria-label*='Description']",
                    ]
                )
                crawled_features = await self._read_first_visible(
                    page,
                    [
                        "input[placeholder*='Features']",
                        "textarea[placeholder*='features']",
                        "input[name='features']",
                        "textarea[name='features']",
                    ]
                )
                crawled_logo = await self._read_first_visible(
                    page,
                    [
                        "input[placeholder*='Logo']",
                        "input[name='logo']",
                        "input[name='logoUrl']",
                    ]
                )

                if not self._is_crawled_value_valid(crawled_tool_name):
                    crawled_tool_name = site_name
                if not self._is_crawled_value_valid(crawled_website_url):
                    crawled_website_url = url
                if not self._is_crawled_value_valid(crawled_docs_url):
                    crawled_docs_url = docs_url
                if not self._is_crawled_value_valid(crawled_description):
                    crawled_description = site_description
                if not self._is_crawled_value_valid(crawled_short_description):
                    crawled_short_description = site_short_description
                if not self._is_crawled_value_valid(crawled_features):
                    crawled_features = features
                if not self._is_crawled_value_valid(crawled_logo):
                    crawled_logo = logo_file_path

                await self.log_audit(
                    "CrawlPreview",
                    "Success",
                    (
                        "StackShare crawl preview: "
                        f"Tool Name={crawled_tool_name or '[empty]'}, "
                        f"Website URL={crawled_website_url or '[empty]'}, "
                        f"Docs URL={crawled_docs_url or '[empty]'}, "
                        f"Short Description={crawled_short_description or '[empty]'}, "
                        f"Description={crawled_description or '[empty]'}, "
                        f"Features={crawled_features or '[empty]'}, "
                        f"Logo={crawled_logo or '[empty]'}"
                    )
                )

                await self.log_audit(
                    "FillForm",
                    "Running",
                    "Đang đồng bộ dữ liệu crawl vào form trước khi submit..."
                )

                await self._fill_first_visible(
                    page,
                    [
                        "input[placeholder*='Tool Name']",
                        "input[name='name']",
                        "input[id='tool_name']",
                        "input[aria-label*='Name']",
                    ],
                    crawled_tool_name
                )
                await self._fill_first_visible(
                    page,
                    [
                        "input[placeholder*='Website URL']",
                        "input[type='url']",
                        "input[name='website']",
                        "input[name='url']",
                        "#website-url",
                    ],
                    crawled_website_url
                )
                await self._fill_first_visible(
                    page,
                    [
                        "input[placeholder*='Docs URL']",
                        "input[placeholder*='Documentation']",
                        "input[name='docs']",
                        "input[name='documentation']",
                    ],
                    crawled_docs_url
                )
                await self._fill_first_visible(
                    page,
                    [
                        "textarea[placeholder='Short description (2-3 sentences) *']",
                        "input[placeholder*='Short description']",
                        "textarea[placeholder*='Short description']",
                        "textarea[placeholder*='description']",
                        "textarea[aria-label*='Description']",
                    ],
                    crawled_short_description
                )
                await self._fill_first_visible(
                    page,
                    [
                        "input[placeholder*='One-line description']",
                        "textarea[placeholder*='Short description']",
                        "textarea[placeholder*='Short description']",
                        "textarea[placeholder*='description']",
                        "textarea[aria-label*='Description']",
                    ],
                    crawled_description
                )
                await self._fill_first_visible(
                    page,
                    [
                        "input[placeholder*='Features']",
                        "textarea[placeholder*='features']",
                        "input[name='features']",
                        "textarea[name='features']",
                    ],
                    crawled_features
                )

                uploaded_logo = await self._upload_logo_file(page, metadata)
                if uploaded_logo:
                    crawled_logo = uploaded_logo

                await self.log_audit(
                    "UserReview",
                    "Running",
                    "Đã đồng bộ dữ liệu crawl. Nếu cần chỉnh sửa thêm, đây là bước review trước khi submit."
                )

                await page.wait_for_timeout(1000)
                await self._wait_for_submit_enabled(page)

                if not await self._click_first_visible(
                    page,
                    [
                        STACKSHARE_SUBMIT_SELECTOR,
                        "button:has-text('Submit')"
                    ]
                ):
                    raise ValueError("Không tìm thấy nút Submit trên StackShare.")

                await page.wait_for_load_state("networkidle")

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit(
                    "Submit",
                    "Success",
                    f"Đã submit thành công lên StackShare. Thời gian: {duration}ms",
                    duration
                )

                return {
                    "success": True,
                    "response_data": json.dumps(
                        {
                            "message": f"Submit thành công công cụ '{crawled_tool_name}' lên StackShare.",
                            "crawled_data": {
                                "tool_name": crawled_tool_name,
                                "website_url": crawled_website_url,
                                "docs_url": crawled_docs_url,
                                "short_description": crawled_short_description,
                                "description": crawled_description,
                                "features": crawled_features,
                                "logo": crawled_logo,
                                "logo_file_path": uploaded_logo or logo_file_path
                            }
                        },
                        ensure_ascii=False
                    ),
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
