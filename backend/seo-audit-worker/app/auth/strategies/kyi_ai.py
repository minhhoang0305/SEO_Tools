from __future__ import annotations

from app.auth.base import BaseAuthStrategy


class KYIAiAuthStrategy(BaseAuthStrategy):
    async def ensure_authenticated(self, browser):
        context_kwargs = {
            "viewport": {"width": 1280, "height": 900},
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        }
        return await browser.new_context(**context_kwargs)
