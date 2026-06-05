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
        url: str
    ):

        http_crawler = HttpCrawler()

        result = await http_crawler.crawl(
            url
        )

        soup = BeautifulSoup(
            result["html"],
            "html.parser"
        )

        images = len(
            soup.find_all("img")
        )

        links = len(
            soup.find_all("a")
        )

        should_render = (
            images == 0
            and
            links == 0
        )

        if not should_render:
            return result

        print(
            "Fallback to Playwright..."
        )

        playwright_crawler = (
            PlaywrightCrawler()
        )

        return await playwright_crawler.crawl(
            url
        )