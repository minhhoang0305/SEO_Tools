from __future__ import annotations

import json
from typing import Dict, Optional


class KYIAiResultParser:
    def format_preview(self, data: Dict[str, str]) -> str:
        return (
            "Kyi AI preview: "
            f"Website Name={data.get('website_name') or '[empty]'}, "
            f"Website URL={data.get('website_url') or '[empty]'}, "
            f"Email={data.get('email') or '[empty]'}"
        )

    def build_preview_payload(self, data: Dict[str, str]) -> str:
        return json.dumps(
            {
                "message": "Kyi AI đã điền xong form. Hãy review trước khi submit.",
                "requires_manual_action": True,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_success_payload(self, data: Dict[str, str], final_url: str = "") -> str:
        return json.dumps(
            {
                "message": "Kyi AI submit hoàn tất.",
                "final_url": final_url,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_pending_payload(self, details: Optional[str] = None) -> str:
        payload = {"message": "Kyi AI submit đang chờ xác nhận.", "submitted": False}
        if details:
            payload["details"] = details
        return json.dumps(payload, ensure_ascii=False)
