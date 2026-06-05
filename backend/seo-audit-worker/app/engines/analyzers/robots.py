import httpx


async def analyze_robots(base_url: str):

    robots_url = f"{base_url}/robots.txt"

    try:

        async with httpx.AsyncClient() as client:

            response = await client.get(
                robots_url,
                follow_redirects=True
            )

            if response.status_code != 200:
                return {
                    "exists": False,
                    "sitemaps": []
                }

            sitemaps = []

            for line in response.text.splitlines():

                line = line.strip()

                if line.lower().startswith("sitemap:"):
                    sitemap = line.split(":",1)[1].strip()

                    sitemaps.append(sitemap)

            return {
                "exists": True,
                "sitemaps": sitemaps
            }

    except Exception as ex:
        print(
            f"ROBOTS ERROR: {ex}"
        )
        return {
            "exists": False,
            "sitemaps": []
        }