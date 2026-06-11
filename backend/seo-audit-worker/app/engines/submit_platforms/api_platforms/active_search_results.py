import time
from app.platforms.api_client import ApiClientHelper
from app.platforms.result_parser import ResultParser
from app.platforms.retry_timeout import RetryTimeoutHandler
from app.engines.submit_platforms.base_handler import BaseSubmitHandler
from typing import Dict, Any

class ActiveSearchResultsSubmitHandler(BaseSubmitHandler):
    async def submit(self, url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        submit_url = "https://www.activesearchresults.com/addwebsite.php"
        api_client = ApiClientHelper(timeout=20.0, follow_redirects=True)
        parser = ResultParser()
        retry_helper = RetryTimeoutHandler(retries=2, delay_seconds=1.0, timeout_seconds=20.0)

        email = metadata.get("ContactEmail") or "test-seo-submit@example.com"
        
        payload = {
            "url": url,
            "email": email
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        await self.log_audit(
            "SubmitRequest", 
            "Running", 
            f"Gửi request POST tới ASR: {submit_url}. Payload: {payload}"
        )

        try:
            response = await retry_helper.run(
                lambda: api_client.post(submit_url, data=payload, headers=headers)
            )
            duration = int((time.time() - start_time) * 1000)

            status_code = response.status_code
            response_text = response.text
            final_url = response.url

            if status_code == 200 and parser.contains_any(
                response_text,
                ["confirm", "added", "urladdedconfirm"]
            ):
                await self.log_audit(
                    "SubmitRequest",
                    "Success",
                    f"Đã chuyển hướng thành công đến trang xác nhận. HTTP Status: {status_code}, Final URL: {final_url}",
                    duration
                )
                return {
                    "success": True,
                    "response_data": f"Status: {status_code}, Final URL: {final_url}",
                    "error_message": None
                }

            err_msg = f"Trang xác nhận phản hồi không chứa nội dung thành công. Status: {status_code}, Final URL: {final_url}."
            await self.log_audit("SubmitRequest", "Failed", err_msg, duration)
            return {
                "success": False,
                "response_data": response_text[:2000],
                "error_message": err_msg
            }
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            err_msg = f"Lỗi kết nối hoặc timeout khi submit lên Active Search Results: {str(e)}"
            await self.log_audit("SubmitRequest", "Failed", err_msg, duration)
            return {
                "success": False,
                "response_data": None,
                "error_message": err_msg
            }
