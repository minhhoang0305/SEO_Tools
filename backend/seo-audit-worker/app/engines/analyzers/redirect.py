import httpx


async def analyze_redirect(url: str):

    redirects = []

    async with httpx.AsyncClient(
        follow_redirects=True
    ) as client:

        response = await client.get(url)

        for item in response.history:

            redirects.append(
                {
                    "status_code": item.status_code,
                    "url": str(item.url)
                }
            )

        return {
            "redirect_count": len(redirects),
            "redirects": redirects,
            "final_url": str(response.url)
        }