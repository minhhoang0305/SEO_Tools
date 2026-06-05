from bs4 import BeautifulSoup

def analyze_language(html: str, response_headers: dict, target_language: str = None):
    try:
        soup = BeautifulSoup(html, "html.parser")
        result = {
            "html_lang": None,
            "http_content_language": response_headers.get("Content-Language") if response_headers else None,
            "hreflang_tag": [],
            "has_x_default": False,
            "status": "Valid",
            "warning": []
        }
        html_tag = soup.find("html")
        if html_tag and html_tag.has_attr("lang"):
            declared_lang = html_tag["lang"]
            result["html_lang"] = declared_lang
            if target_language:
                target_lower = target_language.lower()
                declared_lower = declared_lang.lower()
                # Check if declared language matches target language (e.g. "vi-VN" matches "vi")
                if not declared_lower.startswith(target_lower) and not target_lower.startswith(declared_lower):
                    result["warning"].append(f"Ngôn ngữ khai báo '{declared_lang}' không khớp với ngôn ngữ mục tiêu '{target_language}'")
                    result["status"] = "warning"
        else:
            result["warning"].append("Missing 'lang' attribute in <html> tag")
            result["status"] = "warning"
            
        links = soup.find_all("link", rel="alternate")
        for link in links:
            if link.has_attr("hreflang") and link.has_attr("href"):
                hreflang_val = link["hreflang"]
                href_val = link["href"]

                result["hreflang_tag"].append({"hreflang": hreflang_val, "href": href_val})

                if hreflang_val == "x-default":
                    result["has_x_default"] = True
    
    except Exception as ex:
        print(
            f"LANGUAGE ERROR: {ex}"
        )
    return result
