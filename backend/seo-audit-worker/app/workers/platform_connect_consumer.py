import asyncio
import json
import os

import aio_pika
from playwright.async_api import async_playwright

from app.auth.strategies.stackshare import StackShareAuthStrategy
from app.core.config import RABBITMQ_HOST


class PlatformConnectHandler:
    def __init__(self, platform_info):
        self.platform_info = platform_info
        self.encrypted_credential = None
        self.iv = None

    async def log_audit(self, action, status, content=None, duration_ms=None):
        suffix = f" {duration_ms}ms" if duration_ms is not None else ""
        print(f"[PlatformConnect] {action} ({status}){suffix} {content or ''}")


async def _process_stackshare_connect(message):
    platform_code = (message.get("PlatformCode") or "").lower()
    if platform_code != "stackshare":
        raise ValueError(f"Không hỗ trợ connect cho platform code: {platform_code}")

    handler = PlatformConnectHandler(message)
    strategy = StackShareAuthStrategy(handler)

    async with async_playwright() as p:
        display = os.getenv("DISPLAY", "").strip()
        if not display:
            raise RuntimeError(
                "Thiếu DISPLAY/XServer để mở browser headed. Hãy chạy worker với Xvfb/noVNC."
            )

        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = None
        try:
            await handler.log_audit(
                "BrowserLaunch",
                "Running",
                "Đang mở browser thật để đăng nhập StackShare. Bạn có thể dùng noVNC trên port 6080 để thao tác."
            )
            context = await strategy.bootstrap_connect(browser)
            print("Connect Result: session đã được lưu.")
            return {
                "success": True,
                "response_data": {"message": "Kết nối StackShare thành công."},
                "error_message": None,
            }
        finally:
            if context is not None:
                await context.close()
            await browser.close()


async def run_platform_connect_consumer():
    connection = await aio_pika.connect_robust(host=RABBITMQ_HOST)

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "audit.exchange",
            type=aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        queue = await channel.declare_queue(
            "seo-platform-connect",
            durable=True,
        )

        await queue.bind(
            exchange=exchange,
            routing_key="platform.connect.requested"
        )

        print("Platform Connect Worker: Waiting for messages...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = message.body.decode()
                    try:
                        parsed_message = json.loads(body)
                        print(f"Received Connect Message: {parsed_message}")
                        result = await _process_stackshare_connect(parsed_message)
                        print(f"Connect Result: {result}")
                    except Exception as e:
                        print(f"Error decoding/processing connect message: {e}")


def start_platform_connect_consumer():
    asyncio.run(run_platform_connect_consumer())
