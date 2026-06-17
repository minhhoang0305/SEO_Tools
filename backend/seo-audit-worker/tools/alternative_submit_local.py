from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.engines.submit_platforms.browser_platforms.alternative import AlternativeSubmitHandler


DEFAULT_URL = "https://example.com"


def _pick_icon_file() -> str:
    try:
        from tkinter import Tk, filedialog
    except Exception as exc:
        raise SystemExit(
            "Không mở được hộp thoại chọn ảnh. Hãy truyền --icon-path hoặc cài tkinter cho Python."
        ) from exc

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Chọn folder chứa ảnh icon cho Alternative")
    if not folder:
        root.destroy()
        return ""

    path = filedialog.askopenfilename(
        title="Chọn image icon cho Alternative",
        initialdir=folder,
        filetypes=[
            ("JPEG images", "*.jpg *.jpeg"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Alternative submit locally.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--mode", default="final", choices=["preview", "final"])
    parser.add_argument("--metadata", default="{}")
    parser.add_argument("--software-name", dest="software_name", default="My Software")
    parser.add_argument("--icon-path", dest="icon_path", default="", help="Đường dẫn tới ảnh icon. Bỏ trống để chọn bằng hộp thoại.")
    parser.add_argument("--short-description", dest="short_description", default="A software worth checking out.")
    parser.add_argument("--full-description", dest="full_description", default="A longer software description.")
    parser.add_argument("--homepage-url", dest="homepage_url", default=DEFAULT_URL)
    parser.add_argument("--pricing-url", dest="pricing_url", default="")
    parser.add_argument("--category", default="")
    parser.add_argument("--type", default="SaaS")
    parser.add_argument("--monetization", default="Free")
    parser.add_argument("--status", default="Released")
    parser.add_argument("--platforms", default="")
    parser.add_argument("--features", default="")
    parser.add_argument("--social-links", dest="social_links", default="")
    parser.add_argument("--social-link-type", dest="social_link_type", default="twitter")
    parser.add_argument("--pricing-name", dest="pricing_name", default="")
    parser.add_argument("--pricing-cost", dest="pricing_cost", default="")
    parser.add_argument("--synonyms", default="")
    return parser.parse_args()


async def run() -> dict:
    args = parse_args()
    metadata = json.loads(args.metadata)
    if not isinstance(metadata, dict):
        raise SystemExit("metadata must be a JSON object")

    icon_path = (args.icon_path or "").strip()
    if not icon_path:
        icon_path = _pick_icon_file().strip()
        if not icon_path:
            raise SystemExit("Bạn chưa chọn ảnh icon.")

    metadata.update(
        {
            "SiteName": args.software_name,
            "IconPath": icon_path,
            "ShortDescription": args.short_description,
            "FullDescription": args.full_description,
            "HomepageUrl": args.homepage_url,
            "PricingUrl": args.pricing_url,
            "Category": args.category,
            "Type": args.type,
            "Monetization": args.monetization,
            "Status": args.status,
            "Platforms": args.platforms,
            "Features": args.features,
            "SocialLinks": args.social_links,
            "AlternativeSocialLinkType": args.social_link_type,
            "AlternativePricingName": args.pricing_name,
            "AlternativePricingCost": args.pricing_cost,
            "Synonyms": args.synonyms,
        }
    )

    platform_info = {"PlatformCode": "alternative", "JobDetailId": "00000000-0000-0000-0000-000000000000"}
    handler = AlternativeSubmitHandler(platform_info, db_repo=None)
    return await handler.submit(args.url, metadata, mode=args.mode)


def main() -> None:
    os.environ.setdefault("ALTERNATIVE_DEBUG_HEADFUL", "1")
    result = asyncio.run(run())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
