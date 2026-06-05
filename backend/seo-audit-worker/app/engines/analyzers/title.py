from bs4 import BeautifulSoup

def analyze_title(html: str):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title_tag = soup.find("title")

    if not title_tag:

        return {
            "exists": False,
            "length": 0,
            "value": ""
        }

    title = title_tag.text.strip()

    return {
        "exists": True,
        "value": title,
        "length": len(title)
    }