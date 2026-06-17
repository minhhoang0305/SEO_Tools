from __future__ import annotations

from os import getenv

ALTERNATIVE_SUBMIT_URL = getenv("ALTERNATIVE_SUBMIT_URL", "https://alternative.me/account/submissions")
ALTERNATIVE_LOGIN_URL = getenv("ALTERNATIVE_LOGIN_URL", ALTERNATIVE_SUBMIT_URL)
ALTERNATIVE_SUCCESS_PATTERNS = [
    "thank you",
    "submitted successfully",
    "submission received",
    "we have received",
    "successfully submitted",
]

ALTERNATIVE_FALSE_POSITIVE_PATTERNS = [
    "saved drafts",
    "pending submissions",
    "approved submissions",
    "disapproved submissions",
    "reviews",
    "review",
]

ALTERNATIVE_TYPE_OPTIONS = [
    "desktop",
    "app",
    "online",
]

ALTERNATIVE_MONETIZATION_OPTIONS = [
    "opensource",
    "free",
    "freemium",
    "paid",
]

ALTERNATIVE_STATUS_OPTIONS = [
    "announced",
    "live",
    "abandoned",
    "offline",
]
