from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar


T = TypeVar("T")
AsyncFn = Callable[[], Awaitable[T]]


@dataclass(slots=True)
class RetryTimeoutHandler:
    retries: int = 3
    delay_seconds: float = 2.0
    timeout_seconds: float | None = None

    async def run(self, fn: AsyncFn[T]) -> T:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                if self.timeout_seconds is None:
                    return await fn()
                return await asyncio.wait_for(fn(), timeout=self.timeout_seconds)
            except Exception as exc:
                last_error = exc
                if attempt >= self.retries:
                    raise
                await asyncio.sleep(self.delay_seconds)
        raise last_error or RuntimeError("RetryTimeoutHandler thất bại mà không có exception.")
