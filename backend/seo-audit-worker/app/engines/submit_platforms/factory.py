from typing import Dict, Any
from app.engines.submit_platforms.api_platforms.active_search_results import ActiveSearchResultsSubmitHandler
from app.engines.submit_platforms.browser_platforms.stackshare import StackShareSubmitHandler

class PlatformSubmitFactory:
    @staticmethod
    def get_submit_handler(platform_info: Dict[str, Any], db_repo: Any):
        code = platform_info.get("PlatformCode", "").lower()
        
        if code in ["asr", "active_search_results"]:
            return ActiveSearchResultsSubmitHandler(platform_info, db_repo)
        elif code == "stackshare":
            return StackShareSubmitHandler(platform_info, db_repo)
        else:
            raise ValueError(f"Không hỗ trợ SEO Platform với mã code: {code}")
