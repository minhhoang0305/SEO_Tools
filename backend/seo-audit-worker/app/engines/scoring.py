def calculate(analysis):

    score = 0

    issues = []

    if analysis["https"]:
        score += 20
    else:
        issues.append({
            "severity": "High",
            "title": "HTTPS Missing",
            "description": "The website does not use the secure HTTPS protocol.",
            "recommendation": "Use HTTPS"
        })

    if analysis["title"]:
        score += 20
    else:
        issues.append({
            "severity": "High",
            "title": "Missing Title",
            "description": "The website does not have a <title> tag in the head section.",
            "recommendation": "Add title tag"
        })

    if analysis["meta_description"]:
        score += 20
    else:
        issues.append({
            "severity": "Medium",
            "title": "Missing Meta Description",
            "description": "The website does not have a <meta name=\"description\"> tag in the head section.",
            "recommendation": "Add meta description"
        })

    if analysis["canonical"]:
        score += 20
    else:
        issues.append({
            "severity": "Medium",
            "title": "Missing Canonical",
            "description": "The website does not have a <link rel=\"canonical\"> tag in the head section.",
            "recommendation": "Add canonical tag"
        })

    if analysis["robots"]:
        score += 20
    else:
        issues.append({
            "severity": "Low",
            "title": "Missing Robots Meta",
            "description": "The website does not have a <meta name=\"robots\"> tag in the head section.",
            "recommendation": "Add robots meta"
        })

    return {
        "score": score,
        "issues": issues
    }