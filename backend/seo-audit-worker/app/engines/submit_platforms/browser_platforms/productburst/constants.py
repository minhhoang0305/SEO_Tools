from __future__ import annotations

PRODUCTBURST_BASE_URL = "https://productburst.com"
PRODUCTBURST_HOME_URL = PRODUCTBURST_BASE_URL
PRODUCTBURST_AUTH_URL = f"{PRODUCTBURST_BASE_URL}/auth"
PRODUCTBURST_PRE_LAUNCH_URL = f"{PRODUCTBURST_BASE_URL}/pre-launch"

PRODUCTBURST_LAUNCHPAD_URL_PATTERN = r"/launchpad/(?P<launchpad_id>[A-Za-z0-9x]+)"

PRODUCTBURST_SUCCESS_PATTERNS = [
    "launchpad",
    "launch successful",
    "your launch",
    "scheduled",
    "submitted",
]

