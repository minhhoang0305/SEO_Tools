from __future__ import annotations

import json
from typing import Dict, Optional


class FutureToolsResultParser:
    def format_preview(self, data: Dict[str, str]) -> str:
        return (
            "FutureTools preview: "
            f"Your Name={data.get('your_name') or '[empty]'}, "
            f"Tool Name={data.get('tool_name') or '[empty]'}, "
            f"Tool URL={data.get('tool_url') or '[empty]'}, "
            f"Short Description={data.get('short_description') or '[empty]'}, "
            f"Category={data.get('category') or '[empty]'}, "
            f"Pricing={data.get('pricing') or '[empty]'}, "
            f"Email={data.get('email') or '[empty]'}"
        )

    def build_preview_payload(self, data: Dict[str, str]) -> str:
        return json.dumps(
            {
                "message": "FutureTools đã điền xong form. Hãy review trước khi submit.",
                "requires_manual_action": True,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_success_payload(self, data: Dict[str, str], final_url: str = "") -> str:
        return json.dumps(
            {
                "message": "FutureTools submit hoàn tất.",
                "final_url": final_url,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_pending_payload(self, details: Optional[str] = None) -> str:
        payload = {
            "message": "FutureTools submit đang chờ xác nhận.",
            "submitted": False,
        }
        if details:
            payload["details"] = details
        return json.dumps(payload, ensure_ascii=False)
