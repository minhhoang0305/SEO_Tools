from app.engines.crawles.crawl_factory import (
    CrawlerFactory
)


async def crawl(
    url: str,
    language: str = None,
    country: str = None
):

    return await CrawlerFactory.crawl(
        url,
        language=language,
        country=country
    )