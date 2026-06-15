from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from shutil import which
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.engines.submit_platforms.browser_platforms.futuretools import FutureToolsSubmitHandler


DEFAULT_URL = "https://example.com"


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("FUTURETOOLS_CHROME_EXECUTABLE_PATH", "") or "").strip()
    if raw_value:
        return raw_value

    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path.home() / "Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    for binary in ("google-chrome", "google-chrome-stable", "chrome", "chromium", "chromium-browser"):
        found = which(binary)
        if found:
            return found

    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FutureTools submit locally.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Tool URL sẽ submit lên FutureTools.")
    parser.add_argument("--mode", default="final", choices=["preview", "final"], help="Preview hoặc final submit.")
    parser.add_argument("--metadata", default="{}", help="JSON metadata cho form FutureTools.")
    parser.add_argument("--your-name", dest="your_name", default="Jane Doe", help="Your Name trên form.")
    parser.add_argument("--tool-name", dest="tool_name", default="My AI Tool", help="Tool Name trên form.")
    parser.add_argument("--description", default="An AI tool worth checking out.", help="Short description.")
    parser.add_argument("--category", default="Productivity", help="Category FutureTools.")
    parser.add_argument("--pricing", default="Free", help="Pricing FutureTools.")
    parser.add_argument("--email", default="you@example.com", help="Email người submit.")
    parser.add_argument("--newsletter", action="store_true", help="Tick newsletter checkbox.")
    return parser.parse_args()


async def run() -> Dict[str, Any]:
    args = parse_args()
    try:
        metadata = json.loads(args.metadata)
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be a JSON object")
    except Exception as exc:
        raise SystemExit(f"Metadata không hợp lệ: {exc}") from exc

    metadata.update(
        {
            "YourName": args.your_name,
            "ToolName": args.tool_name,
            "ShortDescription": args.description,
            "Category": args.category,
            "Pricing": args.pricing,
            "ContactEmail": args.email,
            "NewsletterOptIn": "true" if args.newsletter else "false",
        }
    )

    platform_info = {
        "PlatformCode": "futuretools",
        "JobDetailId": "00000000-0000-0000-0000-000000000000",
    }

    handler = FutureToolsSubmitHandler(platform_info, db_repo=None)
    return await handler.submit(args.url, metadata, mode=args.mode)


def main() -> None:
    os.environ.setdefault("FUTURETOOLS_DEBUG_HEADFUL", "1")
    os.environ.setdefault("FUTURETOOLS_WAIT_FOR_MANUAL_VERIFICATION", "1")
    os.environ.setdefault(
        "FUTURETOOLS_PROFILE_DIR",
        str(Path(__file__).resolve().parents[1] / ".playwright" / "futuretools_chrome_profile"),
    )
    chrome_path = get_chrome_executable_path()
    if chrome_path:
        os.environ.setdefault("FUTURETOOLS_CHROME_EXECUTABLE_PATH", chrome_path)
    result = asyncio.run(run())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
