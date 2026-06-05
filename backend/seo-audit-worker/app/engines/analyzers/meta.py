from bs4 import BeautifulSoup


def analyze_meta(html: str):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    meta = soup.find(
        "meta",
        attrs={
            "name": "description"
        }
    )

    if not meta:

        return {
            "exists": False,
            "length": 0,
            "value": ""
        }

    description = meta.get(
        "content",
        ""
    ).strip()

    return {
        "exists": True,
        "value": description,
        "length": len(description)
    }