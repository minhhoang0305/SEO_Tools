import argparse
import asyncio
import platform
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Thiếu dependency 'playwright'. Hãy chạy trong môi trường đã cài backend/seo-audit-worker/requirement.txt "
        "hoặc cài thủ công:\n"
        "  python3 -m pip install -r backend/seo-audit-worker/requirement.txt\n"
        "  python3 -m playwright install chromium"
    ) from exc

STACKSHARE_LOGIN_URL = "https://stackshare.io/"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1]
    / ".playwright"
    / "stackshare_storage_state.json"
)

def get_chrome_profile_path() -> tuple[str, str]:
    """Tự động tìm đường dẫn profile Chrome dựa trên Hệ điều hành"""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        user_data_dir = str(home / "AppData" / "Local" / "Google" / "Chrome" / "User Data")
    elif system == "Darwin":  # macOS
        user_data_dir = str(home / "Library" / "Application Support" / "Google" / "Chrome")
    else:  # Linux
        user_data_dir = str(home / ".config" / "google-chrome")
        
    # Tạo một thư mục tạm phái sinh từ profile gốc để tránh xung đột nếu Chrome đang mở
    playwright_user_data = str(Path(__file__).resolve().parent / ".chrome_profile_tmp")
    return user_data_dir, playwright_user_data

async def connect_stackshare(output_path: Path, timeout_ms: int) -> None:
    async with async_playwright() as p:
        # 1. Lấy thông tin profile Chrome thật
        _, user_data_dir = get_chrome_profile_path()

        # 2. Khởi chạy trình duyệt thật bằng launch_persistent_context
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",  # Bắt buộc: Ép Playwright dùng Google Chrome thật thay vì Chromium
            headless=False,
            viewport={"width": 1280, "height": 800},
            # Loại bỏ flag tự động hóa để tránh bị Google phát hiện
            args=["--disable-blink-features=AutomationControlled"] 
        )
        
        # Lấy trang mặc định tự động mở ra
        page = context.pages[0] if context.pages else await context.new_page()

        await page.goto(
            STACKSHARE_LOGIN_URL,
            wait_until="domcontentloaded",
            timeout=30000,
        )
        print("Trình duyệt Chrome thật đã mở.")
        print("Please login to StackShare bằng GitHub hoặc Google...")
        print("Nếu modal login chưa hiện, hãy bấm Sign in trên trang chủ.")
        print("Chờ đến khi browser chuyển sang /dashboard.")

        await page.wait_for_url("**/", timeout=timeout_ms)

        # Lưu lại trạng thái phiên
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(output_path))
        
        # Đóng ngữ cảnh
        await context.close()
        print(f"Connected. Session đã được lưu tại: {output_path}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Login StackShare locally using real Chrome and save Playwright storage_state."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to save stackshare storage_state JSON.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=300000,
        help="Timeout in milliseconds to wait for dashboard redirect.",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    asyncio.run(connect_stackshare(args.output.expanduser(), args.timeout_ms))

if __name__ == "__main__":
    main()
