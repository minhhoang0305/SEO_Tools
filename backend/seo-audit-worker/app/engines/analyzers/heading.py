from bs4 import BeautifulSoup


def analyze_headings(
    html: str
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    h1s = soup.find_all("h1")
    h2s = soup.find_all("h2")
    h3s = soup.find_all("h3")

    return {
        "h1_count": len(h1s),
        "h2_count": len(h2s),
        "h3_count": len(h3s),

        "h1_texts": [
            h.text.strip()
            for h in h1s
        ]
    }