import asyncio

from app.engines.crawler import crawl
from app.engines.technical_seo import analyze
from app.engines.scoring import calculate


async def main():

    crawl_result = await crawl(
        "https://uplizd.ai/"
    )

    seo_result = analyze(
        crawl_result["html"],
        crawl_result["final_url"]
    )

    print("SEO Analysis")
    print(seo_result)

    score_result = calculate(
        seo_result
    )

    print("SEO Score")
    print(score_result)


asyncio.run(main())