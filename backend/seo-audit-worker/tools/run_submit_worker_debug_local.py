from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.workers.submit_consumer import run_submit_consumer


def _default_chrome_path() -> str:
    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path.home() / "Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return ""


def main() -> None:
    os.environ.setdefault("SUBMIT_WORKER_DEBUG", "1")
    os.environ.setdefault("FUTURETOOLS_DEBUG_HEADFUL", "1")
    os.environ.setdefault("FUTURETOOLS_DEBUG_SLOWMO_MS", "250")
    os.environ.setdefault("ALTERNATIVE_DEBUG_HEADFUL", "1")
    os.environ.setdefault("ALTERNATIVE_DEBUG_SLOWMO_MS", "250")
    os.environ.setdefault("BAITOOLS_DEBUG_HEADFUL", "1")
    os.environ.setdefault("BAITOOLS_DEBUG_SLOWMO_MS", "250")
    os.environ.setdefault("TENWORDS_DEBUG_HEADFUL", "1")
    os.environ.setdefault("TENWORDS_DEBUG_SLOWMO_MS", "250")
    os.environ.setdefault("STACKSHARE_DEBUG_HEADFUL", "1")
    os.environ.setdefault("STACKSHARE_DEBUG_SLOWMO_MS", "250")
    os.environ.setdefault("PRODUCTBURST_DEBUG_HEADFUL", "1")
    os.environ.setdefault("PRODUCTBURST_DEBUG_SLOWMO_MS", "250")
    os.environ.setdefault("BAITOOLS_WAIT_FOR_MANUAL_OAUTH", "1")

    chrome_path = _default_chrome_path()
    if chrome_path:
        os.environ.setdefault("FUTURETOOLS_CHROME_EXECUTABLE_PATH", chrome_path)
        os.environ.setdefault("ALTERNATIVE_CHROME_EXECUTABLE_PATH", chrome_path)
        os.environ.setdefault("BAITOOLS_CHROME_EXECUTABLE_PATH", chrome_path)
        os.environ.setdefault("TENWORDS_CHROME_EXECUTABLE_PATH", chrome_path)
        os.environ.setdefault("STACKSHARE_CHROME_EXECUTABLE_PATH", chrome_path)
        os.environ.setdefault("PRODUCTBURST_CHROME_EXECUTABLE_PATH", chrome_path)

    os.environ.setdefault("FUTURETOOLS_PROFILE_DIR", str(PROJECT_ROOT / ".playwright" / "futuretools_chrome_profile"))
    os.environ.setdefault("FUTURETOOLS_STORAGE_STATE_PATH", str(PROJECT_ROOT / ".playwright" / "futuretools_storage_state.json"))
    os.environ.setdefault("ALTERNATIVE_STORAGE_STATE_PATH", str(PROJECT_ROOT / ".playwright" / "alternative_storage_state.json"))
    os.environ.setdefault("BAITOOLS_STORAGE_STATE_PATH", str(PROJECT_ROOT / ".playwright" / "baitools_storage_state.json"))
    os.environ.setdefault("TENWORDS_PROFILE_DIR", str(PROJECT_ROOT / ".playwright" / "tenwords_chrome_profile"))
    os.environ.setdefault("TENWORDS_STORAGE_STATE_PATH", str(PROJECT_ROOT / ".playwright" / "tenwords_storage_state.json"))
    os.environ.setdefault("STACKSHARE_STORAGE_STATE_PATH", str(PROJECT_ROOT / ".playwright" / "stackshare_storage_state.json"))
    os.environ.setdefault("PRODUCTBURST_STORAGE_STATE_PATH", str(PROJECT_ROOT / ".playwright" / "productburst_storage_state.json"))

    asyncio.run(run_submit_consumer())


if __name__ == "__main__":
    main()
