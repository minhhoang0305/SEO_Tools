from __future__ import annotations

import json
from typing import Dict, Optional


class AlternativeResultParser:
    def format_preview(self, data: Dict[str, str]) -> str:
        return (
            "Alternative preview: "
            f"Software Name={data.get('software_name') or '[empty]'}, "
            f"Homepage URL={data.get('homepage_url') or '[empty]'}, "
            f"Short Description={data.get('short_description') or '[empty]'}, "
            f"Type={data.get('type') or '[empty]'}, "
            f"Monetization={data.get('monetization') or '[empty]'}, "
            f"Status={data.get('status') or '[empty]'}"
        )

    def build_preview_payload(self, data: Dict[str, str]) -> str:
        return json.dumps({"message": "Alternative đã điền xong form. Hãy review trước khi submit.", "requires_manual_action": True, "collected_data": data}, ensure_ascii=False)

    def build_success_payload(self, data: Dict[str, str], final_url: str = "") -> str:
        return json.dumps({"message": "Alternative submit hoàn tất.", "final_url": final_url, "collected_data": data}, ensure_ascii=False)

    def build_pending_payload(self, details: Optional[str] = None) -> str:
        payload = {"message": "Alternative submit đang chờ xác nhận.", "submitted": False}
        if details:
            payload["details"] = details
        return json.dumps(payload, ensure_ascii=False)
