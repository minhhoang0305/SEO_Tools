from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.engines.submit_platforms.browser_platforms.alternative import (
    AlternativeSubmitHandler,
)


async def main():
    os.environ["ALTERNATIVE_DEBUG_HEADFUL"] = "1"
    os.environ["ALTERNATIVE_DEBUG_SLOWMO_MS"] = "500"

    metadata = {
        "SiteName": "My Test Tool",
        "IconPath": "/Users/nolanpham/Desktop/logo.jpg",
        "ShortDescription": "AI assistant for developers and automation workflows.",
        "FullDescription": """
My Test Tool is an AI-powered platform that helps developers automate workflows,
generate content, and improve productivity across multiple business processes.
""",
        "HomepageUrl": "https://example.com",
        "PricingUrl": "https://example.com/pricing",
        "Category": "ai-tools",
        "Type": "online",
        "Monetization": "freemium",
        "Status": "live",
        "Platforms": "Web",
        "Features": "AI,Automation",
        "SocialLinks": "https://twitter.com/example",
        "AlternativeSocialLinkType": "twitter",
        "AlternativePricingName": "Pro",
        "AlternativePricingCost": "29",
        "Synonyms": "AI Assistant",
    }

    platform_info = {
        "PlatformCode": "alternative",
        "JobDetailId": "debug-local"
    }

    handler = AlternativeSubmitHandler(
        platform_info=platform_info,
        db_repo=None
    )

    result = await handler.submit(
        url="https://example.com",
        metadata=metadata,
        mode="final"  # hoặc preview
    )

    print("\nRESULT:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())