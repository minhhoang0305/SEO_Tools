from __future__ import annotations

import json
from typing import Any, Dict, Optional


class TenWordsResultParser:
    def format_preview(self, data: Dict[str, str]) -> str:
        return (
            "10words preview: "
            f"Project Name={data.get('project_name') or '[empty]'}, "
            f"Project URL={data.get('project_url') or '[empty]'}, "
            f"Twitter Handle={data.get('twitter_handle') or '[empty]'}, "
            f"Category={data.get('category') or '[empty]'}, "
            f"Newsletter={data.get('newsletter') or '[empty]'}"
        )

    def build_preview_payload(self, data: Dict[str, str]) -> str:
        return json.dumps(
            {
                "message": "10words đã điền xong form. Hãy review trước khi submit.",
                "requires_manual_action": True,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_success_payload(self, data: Dict[str, str], finish_url: str = "") -> str:
        return json.dumps(
            {
                "message": "10words submit hoàn tất.",
                "final_url": finish_url,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_pending_payload(self, details: Optional[str] = None) -> str:
        payload = {
            "message": "10words submit đang chờ xác nhận.",
            "submitted": False,
        }
        if details:
            payload["details"] = details
        return json.dumps(payload, ensure_ascii=False)
