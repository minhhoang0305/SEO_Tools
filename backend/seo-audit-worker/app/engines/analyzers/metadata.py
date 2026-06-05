from bs4 import BeautifulSoup


def analyze_metadata(html: str, url: str):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title = ""

    if soup.title:
        title = soup.title.text.strip()

    meta_description = ""

    meta = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if meta:
        meta_description = meta.get(
            "content",
            ""
        )

    canonical = ""

    canonical_tag = soup.find(
        "link",
        attrs={"rel": "canonical"}
    )

    if canonical_tag:
        canonical = canonical_tag.get(
            "href",
            ""
        )

    robots = ""

    robots_tag = soup.find(
        "meta",
        attrs={"name": "robots"}
    )

    if robots_tag:
        robots = robots_tag.get(
            "content",
            ""
        )

    return {
        "https": url.startswith("https://"),
        "title": title,
        "meta_description": meta_description,
        "canonical": canonical,
        "robots": robots
    }