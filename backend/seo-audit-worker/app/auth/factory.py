from typing import Any, Dict

from app.auth.base import BaseAuthStrategy
from app.auth.strategies.futuretools import FutureToolsAuthStrategy
from app.auth.strategies.productburst import ProductBurstAuthStrategy
from app.auth.strategies.stackshare import StackShareAuthStrategy


class AuthStrategyFactory:
    @staticmethod
    def get_strategy(platform_info: Dict[str, Any], handler: Any) -> BaseAuthStrategy:
        code = (platform_info.get("PlatformCode") or "").lower()

        if code == "stackshare":
            return StackShareAuthStrategy(handler)
        if code == "productburst":
            return ProductBurstAuthStrategy(handler)
        if code == "futuretools":
            return FutureToolsAuthStrategy(handler)

        raise ValueError(f"Chưa có auth strategy cho platform code: {code}")
