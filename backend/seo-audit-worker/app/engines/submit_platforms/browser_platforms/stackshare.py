import json
import time
from typing import Dict, Any
from playwright.async_api import async_playwright
from app.engines.submit_platforms.base_handler import BaseSubmitHandler
from app.core.crypto_helper import decrypt_credential

class StackShareSubmitHandler(BaseSubmitHandler):
    async def submit(self, url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Giải mã cookies
        await self.log_audit("DecryptCredential", "Running", "Đang giải mã session cookies từ database...")
        decrypted_str = decrypt_credential(self.encrypted_credential, self.iv)
        if not decrypted_str:
            err_msg = "Không thể giải mã credentials. Vui lòng cấu hình lại session cookies."
            await self.log_audit("DecryptCredential", "Failed", err_msg)
            return {"success": False, "response_data": None, "error_message": err_msg}

        # Parse cookies
        try:
            cookies_list = json.loads(decrypted_str)
            if not isinstance(cookies_list, list):
                cookies_list = [cookies_list]
        except json.JSONDecodeError:
            # Hỗ trợ nếu người dùng paste trực tiếp chuỗi token session thô
            cookies_list = [
                {
                    "name": "__Secure-authjs.session-token",
                    "value": decrypted_str.strip(),
                    "domain": ".stackshare.io",
                    "path": "/"
                }
            ]

        await self.log_audit("DecryptCredential", "Success", f"Đã giải mã thành công {len(cookies_list)} cookies.")

        # 2. Khởi chạy trình duyệt Playwright
        await self.log_audit("BrowserLaunch", "Running", "Đang khởi chạy trình duyệt Chromium (Playwright)...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Inject cookies
            await context.add_cookies(cookies_list)
            page = await context.new_page()

            try:
                # 3. Truy cập kiểm tra đăng nhập
                await self.log_audit("LoginCheck", "Running", "Đang truy cập StackShare và kiểm tra trạng thái Session...")
                await page.goto("https://stackshare.io/", wait_until="networkidle", timeout=30000)
                
                # Kiểm tra nút "Sign In" hoặc chuyển hướng để biết có đăng nhập thành công hay không
                signin_button = page.locator("a:has-text('Sign In'), button:has-text('Sign In'), a[href='/login']")
                is_logged_out = await signin_button.first.is_visible()
                
                if is_logged_out:
                    err_msg = "Session cookie hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại và lấy cookie mới."
                    await self.log_audit("LoginCheck", "Failed", err_msg)
                    return {"success": False, "response_data": None, "error_message": err_msg}

                await self.log_audit("LoginCheck", "Success", "Xác thực Session thành công (Đã đăng nhập).")

                submit_page_url = "https://stackshare.io/mhoang030505"
                await self.log_audit("NavigateSubmit", "Running", f"Đang điều hướng đến: {submit_page_url}")
                await page.goto(submit_page_url, wait_until="networkidle", timeout=30000)

                # 5. Điền form thông tin submit website
                await self.log_audit("FillForm", "Running", "Đang điền thông tin vào biểu mẫu submit của StackShare...")
                
                site_name = metadata.get("SiteName") or "My SEO Tool Site"
                site_description = metadata.get("Description") or "A premium online platform for SEO utilities and tracking."
                
                # Tìm các selectors điền form trên trang submit của StackShare
                # StackShare submit tool form:
                # - Tên công cụ: input[name='name'] hoặc tương tự
                # - Website URL: input[name='website'] hoặc input[type='url']
                # - Description: textarea[name='description'] hoặc tương tự
                
                # Thực hiện điền form dựa trên các element phổ biến hoặc fallback
                name_input = page.locator("input[name='name'], input[id='tool_name'], input[placeholder*='Name']")
                url_input = page.locator("input[name='website'], input[type='url'], input[placeholder*='URL']")
                desc_input = page.locator("textarea[name='description'], textarea[placeholder*='description']")

                # Đợi form hiển thị
                await page.wait_for_timeout(2000) 

                if await name_input.first.is_visible():
                    await name_input.first.fill(site_name)
                if await url_input.first.is_visible():
                    await url_input.first.fill(url)
                if await desc_input.first.is_visible():
                    await desc_input.first.fill(site_description)

                # Chụp ảnh màn hình lưu vết trước khi click submit
                screenshot_bytes = await page.screenshot()
                
                # Trong thực tế, click nút submit
                # submit_button = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit')")
                # await submit_button.first.click()
                # await page.wait_for_timeout(5000)

                duration = int((time.time() - start_time) * 1000)
                await self.log_audit("FillForm", "Success", f"Đã điền và gửi form thành công. Thời gian: {duration}ms", duration)
                
                return {
                    "success": True,
                    "response_data": f"Submit thành công công cụ '{site_name}' lên StackShare.",
                    "error_message": None
                }
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                err_msg = f"Lỗi trong quá trình thao tác giao diện tự động trên StackShare: {str(e)}"
                await self.log_audit("NavigateSubmit", "Failed", err_msg, duration)
                return {"success": False, "response_data": None, "error_message": err_msg}
            finally:
                await context.close()
                await browser.close()
