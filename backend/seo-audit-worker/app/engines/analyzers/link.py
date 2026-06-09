from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import httpx
import asyncio
from typing import List, Dict, Any

def analyze_internal_links(
    html: str,
    base_url: str
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    base_domain = urlparse(
        base_url
    ).netloc

    internal_links = set()

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link["href"]

        if href.startswith("/"):

            internal_links.add(
                href
            )
            continue
        parsed = urlparse(href)

        if parsed.netloc == base_domain:

            internal_links.add(
                href
            )
    return {
        "count": len(
            internal_links
        ),
        "links": list(
            internal_links
        )
    }
def analyze_external_links(
    html: str,
    base_url: str
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )
    base_domain = urlparse(
        base_url
    ).netloc
    external_links = set()
    for link in soup.find_all(
        "a",
        href=True
    ):
        href = link["href"]
        parsed = urlparse(href)
        if (
            parsed.netloc
            and
            parsed.netloc != base_domain
        ):

            external_links.add(
                href
            )

    return {
        "count": len(
            external_links
        ),
        "links": list(
            external_links
        )
    }

async def check_url_status(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            response = await client.head(url, timeout=5.0, follow_redirects=True)
            if response.status_code == 405:
                response = await client.get(url, timeout=5.0, follow_redirects=True)
            
            return {
                "url": url,
                "status_code": response.status_code,
                "is_broken": response.status_code >= 400
            }
        except Exception as e:
            return {
                "url": url,
                "status_code": None,
                "is_broken": True,
                "error": str(e)
            }

async def analyze_broken_links(internal_links: List[str], external_links: List[str], base_url: str):
    all_urls_to_check = set()
    
    for link in internal_links:
        full_url = urljoin(base_url, link)
        parsed = urlparse(full_url)
        if parsed.scheme in ("http", "https"):
            all_urls_to_check.add(full_url)
            
    for link in external_links:
        parsed = urlparse(link)
        if parsed.scheme in ("http", "https"):
            all_urls_to_check.add(link)
            
    semaphore = asyncio.Semaphore(10)
    broken_links = []
    
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
        tasks = [check_url_status(client, url, semaphore) for url in all_urls_to_check]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            if res["is_broken"]:
                broken_links.append({
                    "url": res["url"],
                    "status_code": res["status_code"],
                    "error": res.get("error", "")
                })
                
    return {
        "broken_count": len(broken_links),
        "broken_links": broken_links
    }