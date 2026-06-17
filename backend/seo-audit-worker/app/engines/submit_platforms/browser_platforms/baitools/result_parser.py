from __future__ import annotations

import json
from typing import Any, Dict


class BAItoolsResultParser:
    def format_preview(self, data: Dict[str, str]) -> str:
        return (
            "BAI.tools preview: "
            f"AI Tool Name={data.get('tool_name', '')}, "
            f"Website URL={data.get('website_url', '')}"
        )

    def build_preview_payload(self, data: Dict[str, str]) -> Dict[str, Any]:
        return json.dumps(
            {
                "platform": "baitools",
                "status": "preview",
                "data": data,
            },
            ensure_ascii=False,
        )

    def build_success_payload(
        self,
        data: Dict[str, str],
        finish_url: str | None = None,
        finish_text: str | None = None,
        submission_id: int | str | None = None,
    ) -> Dict[str, Any]:
        payload = {
            "platform": "baitools",
            "status": "success",
            "data": data,
        }
        if finish_url:
            payload["finish_url"] = finish_url
        if finish_text:
            payload["finish_text"] = finish_text
        if submission_id is not None:
            payload["id"] = submission_id
        return json.dumps(payload, ensure_ascii=False)

    def build_pending_payload(self, message: str) -> Dict[str, Any]:
        return json.dumps(
            {
                "platform": "baitools",
                "status": "pending",
                "message": message,
            },
            ensure_ascii=False,
        )
