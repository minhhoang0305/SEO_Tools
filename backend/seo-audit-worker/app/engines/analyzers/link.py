from bs4 import BeautifulSoup
from urllib.parse import urlparse

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

        parsed = urlparse(
            href
        )

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