from __future__ import annotations

import json
from typing import Dict, Any, Optional


class StackShareResultParser:
    def format_crawl_preview(self, crawled: Dict[str, str]) -> str:
        return (
            "StackShare crawl preview: "
            f"Tool Name={crawled.get('tool_name') or '[empty]'}, "
            f"Website URL={crawled.get('website_url') or '[empty]'}, "
            f"Docs URL={crawled.get('docs_url') or '[empty]'}, "
            f"Short Description={crawled.get('short_description') or '[empty]'}, "
            f"Description={crawled.get('description') or '[empty]'}, "
            f"Features={crawled.get('features') or '[empty]'}, "
            f"Logo={crawled.get('logo') or '[empty]'}"
        )

    def build_success_payload(self, tool_name: str, crawled: Dict[str, str]) -> str:
        return json.dumps(
            {
                "message": f"Submit thành công công cụ '{tool_name}' lên StackShare.",
                "crawled_data": crawled,
            },
            ensure_ascii=False,
        )

    def build_preview_payload(self, tool_name: str, crawled: Dict[str, str]) -> str:
        return json.dumps(
            {
                "message": f"StackShare đã crawl dữ liệu cho '{tool_name}'. Hãy review và chỉnh sửa trước khi submit.",
                "requires_manual_action": True,
                "crawled_data": crawled,
            },
            ensure_ascii=False,
        )

    def build_submission_pending_payload(self, tool_name: str, details: Optional[str] = None) -> str:
        payload = {
            "message": f"Đã bấm Submit cho '{tool_name}', nhưng chưa xác nhận được trạng thái thành công từ StackShare.",
            "submitted": False,
        }
        if details:
            payload["details"] = details
        return json.dumps(payload, ensure_ascii=False)
