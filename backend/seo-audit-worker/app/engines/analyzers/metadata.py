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

    canonical_tag = soup.find_all(
        "link",
        attrs={"rel": "canonical"}
    )
    canonical_count = len(canonical_tag)
    canonical = ""
    is_absolute = False

    if canonical_count > 0:
        canonical = canonical_tag[0].get("href","").strip()
        is_absolute = canonical.startswith("https") or canonical.startswith("http")

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
        "canonical_count": canonical_count,
        "canonical_absolute": is_absolute,
        "robots": robots
    }