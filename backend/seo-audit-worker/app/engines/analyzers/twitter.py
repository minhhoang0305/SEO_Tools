from bs4 import BeautifulSoup


def analyze_twitter(
    html: str
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    twitter_card = soup.find(
        "meta",
        attrs={
            "name":
                "twitter:card"
        }
    )

    twitter_title = soup.find(
        "meta",
        attrs={
            "name":
                "twitter:title"
        }
    )

    return {
        "has_twitter_card":
            twitter_card is not None,

        "has_twitter_title":
            twitter_title is not None
    }