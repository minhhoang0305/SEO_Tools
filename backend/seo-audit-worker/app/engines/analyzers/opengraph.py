from bs4 import BeautifulSoup


def analyze_opengraph(
    html: str
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    og_title = soup.find(
        "meta",
        property="og:title"
    )

    og_description = soup.find(
        "meta",
        property="og:description"
    )

    og_image = soup.find(
        "meta",
        property="og:image"
    )

    return {
        "has_og_title":
            og_title is not None,

        "has_og_description":
            og_description is not None,

        "has_og_image":
            og_image is not None
    }