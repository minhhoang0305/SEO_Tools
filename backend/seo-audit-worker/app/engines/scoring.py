def calculate(technical_result):

    score = 0

    issues = []

    robots = technical_result["robots"]
    sitemap = technical_result["sitemap"]
    redirect = technical_result["redirect"]
    opengraph = technical_result["opengraph"]
    twitter = technical_result["twitter"]

    if robots["exists"]:
        score += 20
    else:
        issues.append({
            "severity": "High",
            "title": "Missing robots.txt"
        })

    if sitemap["exists"]:
        score += 20
    else:
        issues.append({
            "severity": "High",
            "title": "Missing sitemap.xml"
        })

    if redirect["redirect_count"] <= 2:
        score += 20
    else:
        issues.append({
            "severity": "Medium",
            "title": "Redirect chain too long"
        })

    if (
        opengraph["has_og_title"]
        and
        opengraph["has_og_description"]
        and
        opengraph["has_og_image"]
    ):
        score += 20

    else:

        issues.append({
            "severity": "Medium",
            "title": "Incomplete Open Graph"
        })

    if twitter["has_twitter_card"]:
        score += 20
    else:
        issues.append({
            "severity": "Low",
            "title": "Missing Twitter Card"
        })

    return {
        "score": score,
        "issues": issues
    }