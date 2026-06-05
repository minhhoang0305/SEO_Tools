from playwright.async_api import (
    async_playwright
)


class PlaywrightCrawler:

    async def crawl(
        self,
        url: str,
        language: str = None,
        country: str = None
    ):

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            # Map language to locale
            locale = None
            if language:
                lang_code = language.lower()
                if lang_code == "vi":
                    locale = "vi-VN"
                elif lang_code == "ja":
                    locale = "ja-JP"
                elif lang_code == "en":
                    locale = "en-US"
                else:
                    locale = lang_code

            # Map country to timezone
            timezone_id = None
            if country:
                country_code = country.lower()
                if country_code == "vn":
                    timezone_id = "Asia/Ho_Chi_Minh"
                elif country_code == "us":
                    timezone_id = "America/New_York"
                elif country_code == "jp":
                    timezone_id = "Asia/Tokyo"
                elif country_code == "sg":
                    timezone_id = "Asia/Singapore"

            context_args = {}
            if locale:
                context_args["locale"] = locale
            if timezone_id:
                context_args["timezone_id"] = timezone_id

            context = await browser.new_context(**context_args)
            page = await context.new_page()

            await page.goto(
                url,
                wait_until="networkidle",
                timeout=60000
            )

            html = await page.content()

            final_url = page.url

            await browser.close()

            return {
                "status_code": 200,

                "final_url":
                    final_url,

                "html":
                    html,

                "crawl_method":
                    "playwright"
            }