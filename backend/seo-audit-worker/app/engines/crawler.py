from app.engines.crawles.crawl_factory import (
    CrawlerFactory
)


async def crawl(
    url: str
):

    return await CrawlerFactory.crawl(
        url
    )