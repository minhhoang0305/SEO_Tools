from bs4 import BeautifulSoup

from app.engines.crawles.http_crawl import (
    HttpCrawler
)

from app.engines.crawles.playwright_crawl import (
    PlaywrightCrawler
)


class CrawlerFactory:

    @staticmethod
    async def crawl(
        url: str,
        language: str = None,
        country: str = None
    ):
        should_fallback = False
        result = None

        try:
            http_crawler = HttpCrawler()
            result = await http_crawler.crawl(
                url,
                language=language,
                country=country
            )

            if result.get("status_code") != 200:
                print(f"HTTP crawl returned status code {result.get('status_code')}. Trying Playwright fallback...")
                should_fallback = True
            else:
                soup = BeautifulSoup(
                    result["html"],
                    "html.parser"
                )
                images = len(soup.find_all("img"))
                links = len(soup.find_all("a"))
                if images == 0 and links == 0:
                    print("Empty HTML contents detected. Trying Playwright fallback...")
                    should_fallback = True
        except Exception as ex:
            print(f"HTTP Crawl failed with error: {ex}. Falling back to Playwright...")
            should_fallback = True

        if not should_fallback and result:
            return result

        playwright_crawler = PlaywrightCrawler()
        return await playwright_crawler.crawl(
            url,
            language=language,
            country=country
        )