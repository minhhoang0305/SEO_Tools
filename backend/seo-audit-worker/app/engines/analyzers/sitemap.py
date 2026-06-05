import httpx
import xml.etree.ElementTree as ET


async def analyze_sitemap(
    sitemap_url: str
):

    try:

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True
        ) as client:

            response = await client.get(
                sitemap_url
            )

            if response.status_code != 200:

                return {
                    "exists": False,
                    "status_code": response.status_code,
                    "url_count": 0,
                    "urls": []
                }

            root = ET.fromstring(
                response.text
            )

            namespace = {
                "sm":
                "http://www.sitemaps.org/schemas/sitemap/0.9"
            }

            urls = []

            for loc in root.findall(
                ".//sm:loc",
                namespace
            ):
                urls.append(
                    loc.text.strip()
                )

            return {
                "exists": True,
                "status_code":
                    response.status_code,

                "url_count":
                    len(urls),

                "urls":
                    urls
            }

    except Exception as ex:

        print(
            f"SITEMAP ERROR: {ex}"
        )

        return {
            "exists": False,
            "status_code": None,
            "url_count": 0,
            "urls": []
        }