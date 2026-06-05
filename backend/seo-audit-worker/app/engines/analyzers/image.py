from bs4 import BeautifulSoup


def analyze_images(html: str):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    images = soup.find_all("img")

    total_images = len(images)

    missing_alt = []

    for img in images:

        alt = img.get("alt")

        if not alt or not alt.strip():

            missing_alt.append(
                img.get("src", "")
            )

    return {
        "total_images": total_images,
        "missing_alt_count": len(missing_alt),
        "missing_alt_images": missing_alt
    }