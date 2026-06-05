import httpx


class HttpCrawler:

    async def crawl(
        self,
        url: str,
        language: str = None,
        country: str = None
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

        if language:
            lang_code = language.lower()
            if lang_code == "vi":
                headers["Accept-Language"] = "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
            elif lang_code == "ja":
                headers["Accept-Language"] = "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            elif lang_code == "en":
                headers["Accept-Language"] = "en-US,en;q=0.9"
            else:
                headers["Accept-Language"] = f"{lang_code},en;q=0.9"

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

                "headers":
                    dict(response.headers),

                "html":
                    response.text,

                "crawl_method":
                    "http"
            }