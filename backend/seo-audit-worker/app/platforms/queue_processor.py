from __future__ import annotations

import asyncio
import json
from typing import Awaitable, Callable, Any, Optional

import aio_pika


MessageHandler = Callable[[dict[str, Any]], Awaitable[None]]
ErrorHandler = Callable[[dict[str, Any], Exception], Awaitable[None]]


class QueueJobProcessor:
    def __init__(self, host: str, exchange_name: str, queue_name: str, routing_key: str):
        self.host = host
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key

    async def run(
        self,
        on_message: MessageHandler,
        on_error: Optional[ErrorHandler] = None,
    ) -> None:
        connection = await aio_pika.connect_robust(host=self.host)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                self.exchange_name,
                type=aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            queue = await channel.declare_queue(self.queue_name, durable=True)
            await queue.bind(exchange=exchange, routing_key=self.routing_key)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        payload = json.loads(message.body.decode())
                        try:
                            await on_message(payload)
                        except Exception as exc:
                            if on_error is not None:
                                await on_error(payload, exc)
                            else:
                                raise

    def start(
        self,
        on_message: MessageHandler,
        on_error: Optional[ErrorHandler] = None,
    ) -> None:
        asyncio.run(self.run(on_message, on_error))
