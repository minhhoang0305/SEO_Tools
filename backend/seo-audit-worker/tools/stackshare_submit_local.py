from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.engines.submit_platforms.browser_platforms.stackshare import StackShareSubmitHandler
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Không import được package nội bộ của worker. "
        "Hãy chạy trong thư mục backend/seo-audit-worker và kích hoạt đúng .venv."
    ) from exc


DEFAULT_URL = "https://your-site.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run StackShare submit locally and open Playwright browser immediately."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="Website URL sẽ submit lên StackShare.",
    )
    parser.add_argument(
        "--mode",
        default="final",
        choices=["preview", "final"],
        help="Chạy preview để dừng ở bước crawl hoặc final để đi hết luồng submit.",
    )
    parser.add_argument(
        "--metadata",
        default="{}",
        help="JSON metadata truyền vào submit handler.",
    )
    return parser.parse_args()


async def run() -> Dict[str, Any]:
    args = parse_args()
    try:
        metadata = json.loads(args.metadata)
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be a JSON object")
    except Exception as exc:
        raise SystemExit(f"Metadata không hợp lệ: {exc}") from exc

    platform_info = {
        "PlatformCode": "stackshare",
        "JobDetailId": "00000000-0000-0000-0000-000000000000",
    }

    handler = StackShareSubmitHandler(platform_info, db_repo=None)
    return await handler.submit(args.url, metadata, mode=args.mode)


def main() -> None:
    result = asyncio.run(run())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    os.environ.setdefault("STACKSHARE_DEBUG_HEADFUL", "1")
    main()
