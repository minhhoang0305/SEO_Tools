from __future__ import annotations

import json
from typing import Any, Dict, Optional


class ProductBurstResultParser:
    def format_preview(self, data: Dict[str, str]) -> str:
        return (
            "ProductBurst preview: "
            f"Startup={data.get('startup_name') or '[empty]'}, "
            f"Website={data.get('website_url') or '[empty]'}, "
            f"Tagline={data.get('tagline') or '[empty]'}, "
            f"Description={data.get('product_description') or '[empty]'}, "
            f"Categories={data.get('categories') or '[empty]'}, "
            f"Stacks={data.get('stacks') or '[empty]'}, "
            f"ProductType={data.get('product_type') or '[empty]'}, "
            f"LaunchWeek={data.get('launch_week') or '[empty]'}"
        )

    def build_preview_payload(self, data: Dict[str, str]) -> str:
        return json.dumps(
            {
                "message": "ProductBurst đã đọc xong dữ liệu page 2. Hãy review trước khi launch.",
                "requires_manual_action": True,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_success_payload(
        self,
        data: Dict[str, str],
        launchpad_url: str = "",
        launchpad_id: str = "",
        selected_plan: str = "",
    ) -> str:
        return json.dumps(
            {
                "message": "Launch ProductBurst thành công.",
                "launchpad_url": launchpad_url,
                "launchpad_id": launchpad_id,
                "selected_plan": selected_plan,
                "collected_data": data,
            },
            ensure_ascii=False,
        )

    def build_pending_payload(self, details: Optional[str] = None) -> str:
        payload = {
            "message": "ProductBurst launch đang chờ xác nhận.",
            "submitted": False,
        }
        if details:
            payload["details"] = details
        return json.dumps(payload, ensure_ascii=False)

