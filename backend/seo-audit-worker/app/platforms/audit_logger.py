from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(slots=True)
class AuditEntry:
    action: str
    status: str
    content: Optional[str] = None
    duration_ms: Optional[int] = None


class AuditLogHelper:
    def __init__(self, db_repo: Any = None, detail_id: Any = None):
        self.db_repo = db_repo
        self.detail_id = detail_id

    async def log(
        self,
        action: str,
        status: str,
        content: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        if self.db_repo is not None and self.detail_id is not None:
            await self.db_repo.save_submit_audit_log(
                self.detail_id,
                action,
                status,
                content,
                duration_ms,
            )
            return

        print(f"[Audit] {action} ({status}) {duration_ms or ''}ms {content or ''}")