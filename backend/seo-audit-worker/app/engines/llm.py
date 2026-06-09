import httpx
import json
from typing import Dict, Any, List
from app.core.config import GEMINI_API_KEY

async def generate_ai_seo_suggestions(
    url: str,
    seo_result: Dict[str, Any],
    issues: List[Dict[str, Any]],
    keyword: str = ""
):
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "Chưa cấu hình GEMINI_API_KEY trong biến môi trường."
        }

    title = seo_result.get("title", {}).get("value", "Chưa có tiêu đề")
    meta_desc = seo_result.get("meta", {}).get("value", "Chưa có thẻ mô tả")
    
    headings = seo_result.get("heading", {})
    h1_text = ", ".join(headings.get("h1_texts", []))
    h2_count = headings.get("h2_count", 0)
    h3_count = headings.get("h3_count", 0)
    h2_texts = headings.get("h2_texts", [])
    h3_texts = headings.get("h3_texts", [])

    images = seo_result.get("images", {})
    total_images = images.get("total_images", 0)
    missing_alt = images.get("missing_alt_count", 0)

    web_vitals = seo_result.get("web_vitals", {})
    perf_score = web_vitals.get("performance_score", "N/A")
    lcp = web_vitals.get("field_data", {}).get("lcp_ms", "N/A")
    cls = web_vitals.get("field_data", {}).get("cls", "N/A")

    broken_links_data = seo_result.get("broken_links", {})
    broken_count = broken_links_data.get("broken_count", 0)
    broken_list = [item["url"] for item in broken_links_data.get("broken_links", [])[:10]]
    broken_links_text = ", ".join(broken_list) if broken_list else "Không phát hiện"

    static_issues_text = "\n".join([
        f"- [{issue['severity']}] {issue['title']}: {issue.get('description', '')}"
        for issue in issues
    ])

    prompt = f"""
Bạn là một chuyên gia tối ưu hóa công cụ tìm kiếm (SEO Specialist) kiêm Lập trình viên Web xuất sắc.
Hãy phân tích toàn bộ dữ liệu thu thập (crawled data) dưới đây và tính toán điểm số SEO, đồng thời đề xuất kế hoạch tối ưu chi tiết.

--- THÔNG TIN TRANG WEB ---
- URL: {url}
- Từ khóa mục tiêu: {keyword if keyword else "Chưa cung cấp"}

--- DỮ LIỆU CRAWL CHI TIẾT ---
1. Thẻ Meta & Nội dung:
   - Tiêu đề hiện tại: "{title}"
   - Mô tả hiện tại: "{meta_desc}"
   - Thẻ H1: "{h1_text}"
   - Số lượng thẻ H2: {h2_count} | Số lượng thẻ H3: {h3_count}
   - Các tiêu đề H2 tiêu biểu: {h2_texts[:5]}
   - Các tiêu đề H3 tiêu biểu: {h3_texts[:5]}

2. Hình ảnh:
   - Tổng số hình ảnh: {total_images}
   - Số ảnh bị thiếu thuộc tính Alt: {missing_alt}

3. Trải nghiệm người dùng & Tốc độ (Google Lighthouse / PageSpeed):
   - Điểm hiệu năng (Performance Score): {perf_score}/100
   - Thời gian hiển thị nội dung lớn nhất (LCP): {lcp} ms
   - Điểm thay đổi bố cục tích lũy (CLS): {cls}

4. Liên kết bị gãy (Broken Links):
   - Số lượng link lỗi (404/Connection Error): {broken_count}
   - Danh sách link hỏng: {broken_links_text}

--- DANH SÁCH LỖI TĨNH BỘ QUÉT ĐÃ PHÁT HIỆN ---
{static_issues_text if static_issues_text else "Không phát hiện lỗi kỹ thuật cơ bản nào."}

--- YÊU CẦU ĐÁNH GIÁ & CHẤM ĐIỂM (TRẢ VỀ TIẾNG VIỆT) ---
Hãy phân tích sâu các yếu tố trên và trả về kết quả dưới định dạng JSON theo đúng schema yêu cầu:
1. **score**: Điểm SEO tổng thể (0-100), là trung bình cộng của technical_score và on_page_score.
2. **technical_score**: Điểm kỹ thuật (0-100), chấm dựa trên robots.txt, sitemaps, redirect, SSL (https), và broken links (trừ điểm nặng nếu có link hỏng 404).
3. **on_page_score**: Điểm tối ưu trang (0-100), chấm dựa trên title, meta description, heading structure (H1/H2/H3), tối ưu từ khóa mục tiêu, và ảnh thiếu alt.
4. **issues**: Danh sách các vấn đề phát hiện và hướng khắc phục.
   Với mỗi issue:
   - **severity**: Chọn một trong ["High", "Medium", "Low", "Info", "AI"]
   - **title**: Tiêu đề lỗi/gợi ý ngắn gọn bằng Tiếng Việt.
   - **description**: Giải thích chi tiết tại sao đây là lỗi hoặc điểm cần tối ưu dựa trên dữ liệu crawl.
   - **recommendation**: Hướng dẫn cụ thể hoặc code HTML/SEO cần sửa đổi để lập trình viên thực hiện.

*Lưu ý quan trọng:* Hãy thêm một phần tử issue đặc biệt cuối cùng với `severity` là "AI", `title` là "Báo cáo tối ưu hóa tổng quan từ AI (LLM)", và trường `recommendation` chứa toàn bộ phân tích chi tiết tổng thể (nhận xét chung, đề xuất viết lại Title/Description mẫu, action plan) định dạng Markdown để hiển thị trên Dashboard.
*Yêu cầu độ dài:* Để tránh tràn độ dài cơ sở dữ liệu (giới hạn 4000 ký tự), các trường 'description' và 'recommendation' trong từng phần tử issue bắt buộc phải ngắn gọn, súc tích và KHÔNG VƯỢT QUÁ 3500 ký tự mỗi trường.
"""

    api_url_default = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "score": {"type": "INTEGER"},
                    "technical_score": {"type": "INTEGER"},
                    "on_page_score": {"type": "INTEGER"},
                    "issues": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "severity": {"type": "STRING", "enum": ["High", "Medium", "Low", "Info", "AI"]},
                                "title": {"type": "STRING"},
                                "description": {"type": "STRING"},
                                "recommendation": {"type": "STRING"}
                            },
                            "required": ["severity", "title", "description", "recommendation"]
                        }
                    }
                },
                "required": ["score", "technical_score", "on_page_score", "issues"]
            }
        }
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(api_url_default, json=payload, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Lỗi gọi Gemini API: {response.text}"
                }
                
            data = response.json()
            ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_result = json.loads(ai_text)
            
            return {
                "success": True,
                "score": parsed_result.get("score", 50),
                "technical_score": parsed_result.get("technical_score", 50),
                "on_page_score": parsed_result.get("on_page_score", 50),
                "issues": parsed_result.get("issues", [])
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Lỗi kết nối AI: {str(e)}"
        }
