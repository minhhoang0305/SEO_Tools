def calculate(technical_result, keyword=None, target_language=None):

    technical_score = 0
    on_page_score = 0
    issues = []

    robots = technical_result["robots"]
    sitemap = technical_result["sitemap"]
    redirect = technical_result["redirect"]
    opengraph = technical_result["opengraph"]
    twitter = technical_result["twitter"]
    title = technical_result["title"]
    meta = technical_result["meta"]
    heading = technical_result["heading"]
    images = technical_result["images"]
    languages = technical_result.get("languages", {})

    # --- TECHNICAL SEO RULES (Max 100 points, 20 points per rule) ---

    # 1. Robots.txt
    if robots["exists"]:
        technical_score += 20
    else:
        issues.append({
            "severity": "High",
            "title": "Missing robots.txt",
            "description": "Tệp robots.txt không tồn tại trên website.",
            "recommendation": "Tạo tệp robots.txt ở thư mục gốc của website để hướng dẫn các bot tìm kiếm cách thu thập thông tin."
        })

    # 2. Sitemap.xml
    if sitemap["exists"]:
        technical_score += 20
    else:
        issues.append({
            "severity": "High",
            "title": "Missing sitemap.xml",
            "description": "Sơ đồ trang web sitemap.xml không được tìm thấy.",
            "recommendation": "Tạo tệp sitemap.xml chứa danh sách URL của trang web và khai báo trong robots.txt hoặc Google Search Console."
        })

    # 3. Redirects
    if redirect["redirect_count"] <= 2:
        technical_score += 20
    else:
        issues.append({
            "severity": "Medium",
            "title": "Redirect chain too long",
            "description": f"Có quá nhiều bước chuyển hướng (gồm {redirect['redirect_count']} lượt chuyển hướng) trước khi tải được trang.",
            "recommendation": "Giảm số lượng chuyển hướng trung gian để cải thiện tốc độ tải trang và SEO."
        })

    # 4. Open Graph
    if (
        opengraph["has_og_title"]
        and
        opengraph["has_og_description"]
        and
        opengraph["has_og_image"]
    ):
        technical_score += 20
    else:
        issues.append({
            "severity": "Medium",
            "title": "Incomplete Open Graph",
            "description": "Thiếu các thẻ Open Graph (og:title, og:description, hoặc og:image) dùng để hiển thị khi chia sẻ trên mạng xã hội.",
            "recommendation": "Thêm đầy đủ các thẻ meta Open Graph vào phần <head>."
        })

    # 5. Twitter Card
    if twitter["has_twitter_card"]:
        technical_score += 20
    else:
        issues.append({
            "severity": "Low",
            "title": "Missing Twitter Card",
            "description": "Thiếu thẻ meta Twitter Card cho mạng xã hội Twitter.",
            "recommendation": "Thêm thẻ <meta name=\"twitter:card\" content=\"summary_large_image\"> vào phần <head>."
        })

    # --- ON-PAGE SEO RULES (Max 100 points) ---

    has_keyword = bool(keyword and keyword.strip())

    if has_keyword:
        w_title = 25
        w_meta = 25
        w_h1 = 15
        w_alt = 15
        w_kw_title = 10
        w_kw_meta = 5
        w_kw_h1 = 5
    else:
        w_title = 30
        w_meta = 30
        w_h1 = 20
        w_alt = 20
        w_kw_title = 0
        w_kw_meta = 0
        w_kw_h1 = 0

    # 1. Title Tag
    if title["exists"]:
        title_len = title["length"]
        if 30 <= title_len <= 65:
            on_page_score += w_title
        else:
            on_page_score += w_title // 2
            if title_len < 30:
                issues.append({
                    "severity": "Low",
                    "title": "Title tag is too short",
                    "description": f"Tiêu đề trang quá ngắn (chỉ có {title_len} ký tự).",
                    "recommendation": "Viết tiêu đề dài từ 30 đến 65 ký tự để hiển thị tốt nhất trên kết quả tìm kiếm."
                })
            else:
                issues.append({
                    "severity": "Low",
                    "title": "Title tag is too long",
                    "description": f"Tiêu đề trang quá dài ({title_len} ký tự) và có thể bị cắt bớt trên kết quả tìm kiếm.",
                    "recommendation": "Rút ngắn tiêu đề dưới 65 ký tự để tránh bị cắt cụt."
                })
    else:
        issues.append({
            "severity": "High",
            "title": "Missing Title Tag",
            "description": "Thẻ tiêu đề <title> bị thiếu trong phần head.",
            "recommendation": "Thêm thẻ <title> chứa từ khóa mục tiêu vào phần head của trang."
        })

    # 2. Meta Description
    if meta["exists"]:
        meta_len = meta["length"]
        if 120 <= meta_len <= 160:
            on_page_score += w_meta
        else:
            on_page_score += w_meta // 2
            if meta_len < 120:
                issues.append({
                    "severity": "Low",
                    "title": "Meta description is too short",
                    "description": f"Thẻ mô tả quá ngắn (chỉ có {meta_len} ký tự).",
                    "recommendation": "Viết mô tả dài hơn (từ 120 đến 160 ký tự) để mô tả tốt hơn nội dung trang web."
                })
            else:
                issues.append({
                    "severity": "Low",
                    "title": "Meta description is too long",
                    "description": f"Thẻ mô tả quá dài ({meta_len} ký tự) và có thể bị cắt bớt trên Google.",
                    "recommendation": "Rút ngắn thẻ mô tả dưới 160 ký tự."
                })
    else:
        issues.append({
            "severity": "High",
            "title": "Missing Meta Description",
            "description": "Thẻ mô tả (meta description) bị thiếu.",
            "recommendation": "Thêm thẻ <meta name=\"description\" content=\"...\"> với độ dài từ 120 đến 160 ký tự."
        })

    # 3. Heading (H1)
    h1_count = heading.get("h1_count", 0)
    if h1_count == 1:
        on_page_score += w_h1
    elif h1_count == 0:
        issues.append({
            "severity": "High",
            "title": "Missing H1 Heading",
            "description": "Trang web không có thẻ tiêu đề H1 nào.",
            "recommendation": "Thêm chính xác một thẻ H1 chứa từ khóa chính để cấu trúc trang được rõ ràng."
        })
    else:
        on_page_score += w_h1 // 2
        issues.append({
            "severity": "Medium",
            "title": "Multiple H1 Headings",
            "description": f"Trang web có nhiều thẻ H1 ({h1_count} thẻ).",
            "recommendation": "Chỉ sử dụng duy nhất một thẻ H1 cho tiêu đề chính, các tiêu đề phụ nên chuyển thành H2 hoặc H3."
        })

    # 4. Image alt
    total_imgs = images.get("total_images", 0)
    missing_alt = images.get("missing_alt_count", 0)
    if total_imgs > 0:
        if missing_alt == 0:
            on_page_score += w_alt
        else:
            alt_score = int(((total_imgs - missing_alt) / total_imgs) * w_alt)
            on_page_score += alt_score
            issues.append({
                "severity": "Medium",
                "title": "Images missing alt attribute",
                "description": f"Có {missing_alt}/{total_imgs} hình ảnh bị thiếu thuộc tính alt.",
                "recommendation": "Bổ sung thuộc tính alt (văn bản thay thế) cho các hình ảnh để tối ưu hóa SEO hình ảnh."
            })
    else:
        on_page_score += w_alt

    # 5. Keyword Optimization
    if has_keyword:
        kw_lower = keyword.strip().lower()

        # Keyword in Title
        title_val = title.get("value", "") if title["exists"] else ""
        if title_val and kw_lower in title_val.lower():
            on_page_score += w_kw_title
        else:
            issues.append({
                "severity": "Medium",
                "title": "Keyword not in Title tag",
                "description": f"Từ khóa mục tiêu '{keyword}' không xuất hiện trong thẻ tiêu đề <title>.",
                "recommendation": "Chèn từ khóa mục tiêu vào thẻ tiêu đề, tốt nhất là đặt ở đầu tiêu đề để tăng sự liên quan."
            })

        # Keyword in Meta Description
        meta_val = meta.get("value", "") if meta["exists"] else ""
        if meta_val and kw_lower in meta_val.lower():
            on_page_score += w_kw_meta
        else:
            issues.append({
                "severity": "Low",
                "title": "Keyword not in Meta Description",
                "description": f"Từ khóa mục tiêu '{keyword}' không xuất hiện trong thẻ mô tả (Meta Description).",
                "recommendation": "Chèn từ khóa mục tiêu một cách tự nhiên vào nội dung thẻ mô tả để tăng tỷ lệ click (CTR)."
            })

        # Keyword in H1
        h1_texts = heading.get("h1_texts", [])
        if any(kw_lower in h.lower() for h in h1_texts):
            on_page_score += w_kw_h1
        else:
            issues.append({
                "severity": "Low",
                "title": "Keyword not in H1 tag",
                "description": f"Từ khóa mục tiêu '{keyword}' không xuất hiện trong tiêu đề chính H1.",
                "recommendation": "Chèn từ khóa mục tiêu vào tiêu đề chính H1 của trang web."
            })

    # 6. Language Warnings
    if languages:
        for warning in languages.get("warning", []):
            on_page_score -= 5
            if "lang" in warning.lower() and "missing" in warning.lower():
                issues.append({
                    "severity": "Medium",
                    "title": "Missing lang attribute in html tag",
                    "description": "Thẻ <html> thiếu thuộc tính 'lang' khai báo ngôn ngữ của trang.",
                    "recommendation": "Thêm thuộc tính lang vào thẻ <html> (ví dụ: <html lang=\"vi\">)."
                })
            else:
                issues.append({
                    "severity": "Medium",
                    "title": "Language mismatch",
                    "description": warning,
                    "recommendation": "Cập nhật thuộc tính lang của thẻ <html> cho khớp với ngôn ngữ phân tích mục tiêu."
                })

    on_page_score = max(0, min(100, on_page_score))

    # Calculate overall SEO score (average of technical and on-page score)
    seo_score = int((technical_score + on_page_score) / 2)

    return {
        "score": seo_score,
        "technical_score": technical_score,
        "on_page_score": on_page_score,
        "issues": issues
    }