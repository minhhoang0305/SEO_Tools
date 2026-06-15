from abc import abstractmethod

from app.auth.factory import AuthStrategyFactory
from app.engines.submit_platforms.base_handler import BaseSubmitHandler


class BaseBrowserSubmitHandler(BaseSubmitHandler):
    auth_strategy_cls = None

    def build_auth_strategy(self):
        if self.auth_strategy_cls is not None:
            return self.auth_strategy_cls(self)
        return AuthStrategyFactory.get_strategy(self.platform_info, self)

    async def create_authenticated_context(self, browser):
        strategy = self.build_auth_strategy()
        return await strategy.ensure_authenticated(browser)

    @abstractmethod
    async def submit(self, url, metadata, mode: str = "final"):
        raise NotImplementedError
