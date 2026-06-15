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
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return ""


def main() -> None:
    os.environ.setdefault("FUTURETOOLS_DEBUG_HEADFUL", "1")
    os.environ.setdefault("FUTURETOOLS_CHROME_EXECUTABLE_PATH", _default_chrome_path())
    os.environ.setdefault("FUTURETOOLS_PROFILE_DIR", str(PROJECT_ROOT / ".playwright" / "futuretools_chrome_profile"))
    os.environ.setdefault("FUTURETOOLS_STORAGE_STATE_PATH", str(PROJECT_ROOT / ".playwright" / "futuretools_storage_state.json"))
    asyncio.run(run_submit_consumer())


if __name__ == "__main__":
    main()
