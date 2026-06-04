import httpx

async def crawl(url: str):

    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True
    ) as client:

        response = await client.get(url)

        return {
            "status_code": response.status_code,
            "final_url": str(response.url),
            "html": response.text
        }