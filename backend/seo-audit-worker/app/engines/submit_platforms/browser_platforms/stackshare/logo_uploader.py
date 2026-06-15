from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict


class StackShareLogoUploader:
    def __init__(self, handler: Any):
        self.handler = handler

    def resolve_logo_file_path(self, metadata: Dict[str, Any]) -> str:
        candidate_keys = [
            "LogoPath",
            "LogoFilePath",
            "LogoFile",
            "LogoLocalPath",
        ]

        for key in candidate_keys:
            value = (metadata.get(key) or "").strip()
            if value and Path(value).expanduser().exists():
                return str(Path(value).expanduser())

        logo_url = (metadata.get("LogoUrl") or metadata.get("Logo") or "").strip()
        if logo_url and Path(logo_url).expanduser().exists():
            return str(Path(logo_url).expanduser())

        return ""

    async def upload(self, page, metadata: Dict[str, Any]) -> str:
        logo_file_path = self.resolve_logo_file_path(metadata)
        if not logo_file_path:
            logo_url = (metadata.get("LogoUrl") or metadata.get("Logo") or "").strip()
            if logo_url:
                await self.handler.log_audit(
                    "LogoUpload",
                    "Running",
                    "Logo được cung cấp dưới dạng URL, nhưng StackShare cần file local để upload. Bỏ qua logo."
                )
            return ""

        file_input_locator = page.locator("input[type='file'][accept*='image'], input[type='file']")
        if await file_input_locator.count() == 0:
            raise ValueError("Không tìm thấy input upload logo trên StackShare.")

        await file_input_locator.first.set_input_files(logo_file_path)
        await page.wait_for_timeout(1000)

        await self.handler.log_audit(
            "LogoUpload",
            "Success",
            f"Đã upload logo từ file local: {os.path.basename(logo_file_path)}"
        )
        return logo_file_path