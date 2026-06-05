from playwright.async_api import (
    async_playwright
)


class PlaywrightCrawler:

    async def crawl(
        self,
        url: str
    ):

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            page = await browser.new_page()

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