from __future__ import annotations

import argparse
import asyncio
import os
import sys
import re
from pathlib import Path
from shutil import which

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường backend/seo-audit-worker đã cài requirements."
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://spiff.store/"
DEFAULT_OUTPUT = PROJECT_ROOT / ".playwright" / "spiffstore_submit_storage_state.json"
DEFAULT_SCREENSHOT = PROJECT_ROOT / ".playwright" / "spiffstore_submit_manual.png"
DEFAULT_PROFILE_DIR = PROJECT_ROOT / ".playwright" / "spiffstore_submit_profile"


def get_chrome_executable_path() -> str | None:
    raw_value = (os.getenv("SPIFFSTORE_CHROME_EXECUTABLE_PATH", "") or "").strip()
    if raw_value and Path(raw_value).expanduser().exists():
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
        if found and Path(found).exists():
            return found

    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open Spiff Store submit form in real Chrome, optionally fill sample data, then save screenshot/storage_state."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="URL sẽ mở.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path lưu storage_state JSON.")
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT, help="Path lưu screenshot PNG.")
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR, help="Chrome profile dir dùng cho Playwright.")
    parser.add_argument("--headless", action="store_true", help="Chạy ẩn browser.")
    parser.add_argument("--no-open-form", action="store_true", help="Không tự bấm nút mở form submit.")
    parser.add_argument("--email", default="", help="Email để điền vào form.")
    parser.add_argument("--tool-name", default="", help="Tool Name để điền vào form.")
    parser.add_argument("--website-url", default="", help="Website Url để điền vào form.")
    parser.add_argument("--short-description", default="", help="Short Description để điền vào form.")
    parser.add_argument("--long-description", default="", help="Long Description để điền vào form.")
    parser.add_argument("--seo-title", default="", help="SEO title để điền vào form.")
    parser.add_argument("--meta-description", default="", help="Meta Description để điền vào form.")
    parser.add_argument("--category", default="", help="Category để điền vào form.")
    parser.add_argument("--banner-image-url", default="", help="Website Banner Image URL để điền vào form.")
    parser.add_argument("--auto-submit", action="store_true", help="Tự bấm nút submit sau khi điền xong.")
    parser.add_argument(
        "--step-by-step",
        action="store_true",
        help="Dừng lại sau từng field để bạn theo dõi quá trình nhập.",
    )
    return parser.parse_args()


async def _click_submit_button(page) -> bool:
    selectors = [
        "button:has-text('Submit AI Tool')",
        "button:has-text('Submit Tool')",
        "a:has-text('Submit AI Tool')",
        "a:has-text('Submit Tool')",
        "text=Submit AI Tool",
        "text=Submit Tool",
    ]
    for selector in selectors:
        locator = page.locator(selector)
        if await locator.count() == 0:
            continue
        try:
            target = locator.first
            await target.scroll_into_view_if_needed(timeout=2000)
            await target.click()
            return True
        except Exception:
            continue
    return False


async def _fill_if_provided(page, label_regex: str, selectors: list[str], value: str) -> bool:
    if not value:
        return False

    try:
        field = page.get_by_label(re.compile(label_regex, re.IGNORECASE))
        if await field.count() > 0:
            await field.first.fill(value)
            return True
    except Exception:
        pass

    for selector in selectors:
        locator = page.locator(selector)
        if await locator.count() == 0:
            continue
        try:
            target = locator.first
            await target.scroll_into_view_if_needed(timeout=2000)
            await target.fill(value)
            return True
        except Exception:
            continue
    return False


async def _click_button_if_present(page, button_texts: list[str]) -> bool:
    for text in button_texts:
        selectors = [
            f"button:has-text('{text}')",
            f"a:has-text('{text}')",
            f"span:has-text('{text}')",
            f"text={text}",
        ]
        for selector in selectors:
            locator = page.locator(selector)
            if await locator.count() == 0:
                continue
            try:
                target = locator.first
                await target.scroll_into_view_if_needed(timeout=2000)
                await target.click()
                return True
            except Exception:
                continue
    return False


async def _click_first_submit_like_button(page) -> bool:
    selectors = [
        "button[type='submit']",
        "button:has-text('Submit')",
        "button:has-text('Save')",
        "button:has-text('Publish')",
        "input[type='submit']",
    ]
    for selector in selectors:
        locator = page.locator(selector)
        if await locator.count() == 0:
            continue
        try:
            target = locator.first
            await target.scroll_into_view_if_needed(timeout=2000)
            await target.click()
            return True
        except Exception:
            continue
    return False


def _pause_step(enabled: bool, message: str) -> None:
    if not enabled:
        return
    input(f"{message}\nNhấn Enter để đi tiếp... ")


async def _fill_text_field(page, label: str, value: str, selectors: list[str]) -> bool:
    return await _fill_if_provided(page, label, selectors, value)


async def _fill_select_field(page, label: str, value: str, selectors: list[str]) -> bool:
    if not value:
        return False

    try:
        field = page.get_by_label(re.compile(label, re.IGNORECASE))
        if await field.count() > 0:
            target = field.first
            await target.select_option(value)
            return True
    except Exception:
        pass

    for selector in selectors:
        locator = page.locator(selector)
        if await locator.count() == 0:
            continue
        try:
            target = locator.first
            await target.scroll_into_view_if_needed(timeout=2000)
            await target.select_option(value)
            return True
        except Exception:
            continue
    return False


async def open_spiffstore(
    url: str,
    output_path: Path,
    screenshot_path: Path,
    profile_dir: Path,
    headless: bool,
    open_form: bool,
    auto_submit: bool,
    step_by_step: bool,
    seed: dict[str, str],
) -> None:
    async with async_playwright() as p:
        profile_dir.mkdir(parents=True, exist_ok=True)
        launch_kwargs = {
            "user_data_dir": str(profile_dir),
            "headless": headless,
            "viewport": {"width": 1440, "height": 1000},
            "args": ["--disable-blink-features=AutomationControlled"],
        }

        executable_path = get_chrome_executable_path()
        if executable_path:
            launch_kwargs["executable_path"] = executable_path
        else:
            launch_kwargs["channel"] = "chrome"

        context = await p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.pages[0] if context.pages else await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if open_form:
                opened = await _click_submit_button(page)
                if not opened:
                    print("Không tìm thấy nút mở form submit. Bạn có thể mở thủ công trong browser.")
                else:
                    await page.wait_for_timeout(1000)

            await _fill_text_field(
                page,
                "Email",
                seed.get("email", ""),
                [
                    "input[placeholder*='Email']",
                    "input[type='email']",
                    "input[name='email']",
                ],
            )
            _pause_step(step_by_step, "Đã điền Email")
            await _fill_text_field(
                page,
                "Tool Name",
                seed.get("tool_name", ""),
                [
                    "input[placeholder*='Tool Name']",
                    "input[name='tool_name']",
                    "input[type='text']",
                ],
            )
            _pause_step(step_by_step, "Đã điền Tool Name")
            await _fill_text_field(
                page,
                "Website Url",
                seed.get("website_url", ""),
                [
                    "input[placeholder*='Website']",
                    "input[placeholder*='URL']",
                    "input[name='website_url']",
                    "input[type='url']",
                ],
            )
            _pause_step(step_by_step, "Đã điền Website Url")
            await _fill_text_field(
                page,
                "Short Description",
                seed.get("short_description", ""),
                [
                    "textarea[placeholder*='Short']",
                    "textarea[name='short_description']",
                    "textarea",
                ],
            )
            _pause_step(step_by_step, "Đã điền Short Description")

            next_clicked = await _click_button_if_present(page, ["Next"])
            if next_clicked:
                _pause_step(step_by_step, "Đã bấm Next và mở sang bước tiếp theo")
                await page.wait_for_timeout(1000)
                await _fill_text_field(
                    page,
                    "Long Description",
                    seed.get("long_description", ""),
                    [
                        "textarea[placeholder*='Long']",
                        "textarea[name='long_description']",
                        "textarea",
                    ],
                )
                _pause_step(step_by_step, "Đã điền Long Description")
                await _fill_text_field(
                    page,
                    "SEO title",
                    seed.get("seo_title", ""),
                    [
                        "input[placeholder*='SEO']",
                        "input[name='seo_title']",
                        "input[type='text']",
                    ],
                )
                _pause_step(step_by_step, "Đã điền SEO title")
                await _fill_text_field(
                    page,
                    "Meta Description",
                    seed.get("meta_description", ""),
                    [
                        "textarea[placeholder*='Meta']",
                        "textarea[name='meta_description']",
                        "textarea",
                    ],
                )
                _pause_step(step_by_step, "Đã điền Meta Description")
                filled = await _fill_text_field(
                    page,
                    "Category",
                    seed.get("category", ""),
                    [
                        "input[placeholder*='Category']",
                        "input[name='category']",
                        "textarea[placeholder*='Category']",
                        "textarea[name='category']",
                        "input[type='text']",
                        "textarea",
                    ],
                )
                if not filled and seed.get("category"):
                    filled = await _fill_select_field(
                        page,
                        "Category",
                        seed.get("category", ""),
                        [
                            "select[name='category']",
                            "select",
                        ],
                    )
                if seed.get("category") and not filled:
                    print("Không tìm thấy Category trên trang hiện tại.")
                _pause_step(step_by_step, "Đã điền Category")
                await _fill_text_field(
                    page,
                    "Website Banner Image URL",
                    seed.get("banner_image_url", ""),
                    [
                        "input[placeholder*='Banner']",
                        "input[placeholder*='Image URL']",
                        "input[name='banner_image_url']",
                        "input[type='url']",
                        "input[type='text']",
                    ],
                )
                _pause_step(step_by_step, "Đã điền Website Banner Image URL")

            if auto_submit:
                submitted = await _click_first_submit_like_button(page)
                if submitted:
                    await page.wait_for_timeout(1500)
                else:
                    print("Không tìm thấy nút submit để tự bấm.")
            else:
                print(f"Đã mở: {url}")
                print("Bạn có thể tự thao tác trong browser.")
                print("Khi xong, quay lại terminal và nhấn Enter để chụp screenshot + lưu session.")
                input()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=True)
            await context.storage_state(path=str(output_path))

            print(f"Đã lưu screenshot: {screenshot_path}")
            print(f"Đã lưu storage_state: {output_path}")
            print(f"Chrome profile: {profile_dir}")
        finally:
            await context.close()


def main() -> None:
    args = parse_args()
    asyncio.run(
        open_spiffstore(
            args.url,
            args.output.expanduser(),
            args.screenshot.expanduser(),
            args.profile_dir.expanduser(),
            args.headless,
            not args.no_open_form,
            args.auto_submit,
            args.step_by_step,
            {
                "email": args.email,
                "tool_name": args.tool_name,
                "website_url": args.website_url,
                "short_description": args.short_description,
                "long_description": args.long_description,
                "seo_title": args.seo_title,
                "meta_description": args.meta_description,
                "category": args.category,
                "banner_image_url": args.banner_image_url,
            },
        )
    )


if __name__ == "__main__":
    main()
