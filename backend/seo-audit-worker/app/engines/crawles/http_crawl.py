import httpx


class HttpCrawler:

    async def crawl(
        self,
        url: str
    ):

        headers = {
            "User-Agent":
            (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        }

        async with httpx.AsyncClient(
            headers=headers,
            timeout=30,
            follow_redirects=True
        ) as client:

            response = await client.get(
                url
            )

            return {
                "status_code":
                    response.status_code,

                "final_url":
                    str(response.url),

                "html":
                    response.text,

                "crawl_method":
                    "http"
            }