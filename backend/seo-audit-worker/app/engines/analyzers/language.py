from bs4 import BeautifulSoup
import httpx

def analyze_language(html: str, response_headers: dict):
    try:
        soup = BeautifulSoup(html, "html.parser")
        result = {
            "html_lang": None,
            "http_content_language": response_headers.get("Content-Language"),
            "hreflang_tag": [],
            "has_x_default": False,
            "status": "Valid",
            "warning": []
        }
        html_tag = soup.find("html")
        if html_tag and html_tag.has_attr("lang"):
            result["html_lang"] == result["lang"]
        else:
            result["warning"].append("Missing 'lang' attribute in <html> tag")
            result["status"] = "warning"
        links = soup.findall("link", rel="alternate")
        for link in links:
            if link.has_attr("hreflang") and link.has_attr("href"):
                hreflang_val = link["hreflang"]
                href_val = link["href"]

                result["hreflang_tag"].append({"hreflang":hreflang_val, "href":href_val})

                if hreflang_val == "has_x_default":
                    result["has_x_default"] == True
    
    except Exception as ex:
        print(
            f"SITEMAP ERROR: {ex}"
        )
    return result
