from __future__ import annotations

import json
from typing import Dict, Optional


class AwesomeIndieResultParser:
    def format_preview(self, data: Dict[str, str]) -> str:
        return (
            "Awesome Indie preview: "
            f"Product Name={data.get('product_name') or '[empty]'}, "
            f"URL={data.get('url') or '[empty]'}, "
            f"Tagline={data.get('tagline') or '[empty]'}, "
            f"Categories={data.get('categories') or '[empty]'}, "
            f"Description={data.get('description') or '[empty]'}"
        )

    def build_preview_payload(self, data: Dict[str, str]) -> str:
        return json.dumps(
            {
                "message": "Awesome Indie đã điền xong form. Hãy review trước khi submit.",
                "requires_manual_action": True,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_success_payload(self, data: Dict[str, str], final_url: str = "") -> str:
        return json.dumps(
            {
                "message": "Awesome Indie submit hoàn tất.",
                "final_url": final_url,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_pending_payload(self, details: Optional[str] = None) -> str:
        payload = {"message": "Awesome Indie submit đang chờ xác nhận.", "submitted": False}
        if details:
            payload["details"] = details
        return json.dumps(payload, ensure_ascii=False)

