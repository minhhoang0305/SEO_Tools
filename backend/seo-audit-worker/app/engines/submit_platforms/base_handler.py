from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSubmitHandler(ABC):
    def __init__(self, platform_info: Dict[str, Any], db_repo: Any):
        self.platform_info = platform_info
        self.db_repo = db_repo
        self.detail_id = platform_info.get("JobDetailId")
        self.platform_id = platform_info.get("PlatformId")
        self.platform_code = platform_info.get("PlatformCode")
        self.encrypted_credential = platform_info.get("EncryptedCredential")
        self.iv = platform_info.get("IV")

    @abstractmethod
    async def submit(self, url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực hiện gửi URL lên SEO platform và trả về kết quả dưới dạng:
        {
            "success": True/False,
            "response_data": "...",
            "error_message": "..."
        }
        """
        pass

    async def log_audit(self, action: str, status: str, content: str = None, duration_ms: int = None):
        """
        Ghi nhận nhật ký kiểm toán (audit log) vào database.
        """
        try:
            await self.db_repo.save_submit_audit_log(
                self.detail_id,
                action,
                status,
                content,
                duration_ms
            )
        except Exception as e:
            print(f"Lỗi ghi nhận audit log cho Detail {self.detail_id}: {e}")
