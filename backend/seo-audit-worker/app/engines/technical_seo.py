import asyncio
from urllib.parse import urlparse

from app.engines.analyzers.heading import analyze_headings
from app.engines.analyzers.image import analyze_images
from app.engines.analyzers.language import analyze_language
from app.engines.analyzers.link import (
    analyze_external_links,
    analyze_internal_links,
)
from app.engines.analyzers.meta import analyze_meta
from app.engines.analyzers.metadata import analyze_metadata
from app.engines.analyzers.opengraph import analyze_opengraph
from app.engines.analyzers.redirect import analyze_redirect
from app.engines.analyzers.robots import analyze_robots
from app.engines.analyzers.schema import analyze_schema
from app.engines.analyzers.sitemap import analyze_sitemap
from app.engines.analyzers.title import analyze_title
from app.engines.analyzers.twitter import analyze_twitter
from app.engines.analyzers.web_vitals import analyze_web_vitals


async def analyze_technical_seo(crawl_result, target_language: str = None):
    html_content = crawl_result["html"]
    url = crawl_result["final_url"]

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    robots_task = analyze_robots(base_url)
    redirect_task = analyze_redirect(url)

    robots, redirect = await asyncio.gather(robots_task, redirect_task)

    sitemap = {"exists": False, "data": []}
    if robots.get("sitemaps"):
        sitemap = await analyze_sitemap(robots["sitemaps"][0])

    metadata = analyze_metadata(html_content, url)
    opengraph = analyze_opengraph(html_content)
    twitter = analyze_twitter(html_content)
    title = analyze_title(html_content)
    heading = analyze_headings(html_content)
    meta = analyze_meta(html_content)
    schema = analyze_schema(html_content)
    images = analyze_images(html_content)
    internal_links = analyze_internal_links(html_content, url)
    external_links = analyze_external_links(html_content, url)
    web_vitals = await analyze_web_vitals(url)

    response_headers = crawl_result.get("headers", {})
    language = analyze_language(html_content, response_headers=response_headers, target_language=target_language)

    return {
        "metadata": metadata,
        "robots": robots,
        "sitemap": sitemap,
        "redirect": redirect,
        "opengraph": opengraph,
        "twitter": twitter,
        "title": title,
        "heading": heading,
        "meta": meta,
        "schema": schema,
        "images": images,
        "internal_links": internal_links,
        "external_links": external_links,
        "languages": language,
        "web_vitals": web_vitals   
    }
