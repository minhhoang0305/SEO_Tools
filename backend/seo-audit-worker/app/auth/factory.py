from typing import Any, Dict

from app.auth.base import BaseAuthStrategy
from app.auth.strategies.stackshare import StackShareAuthStrategy


class AuthStrategyFactory:
    @staticmethod
    def get_strategy(platform_info: Dict[str, Any], handler: Any) -> BaseAuthStrategy:
        code = (platform_info.get("PlatformCode") or "").lower()

        if code == "stackshare":
            return StackShareAuthStrategy(handler)

        raise ValueError(f"Chưa có auth strategy cho platform code: {code}")
