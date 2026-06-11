STACKSHARE_SUBMIT_URL = "https://stackshare.io/"
STACKSHARE_LIST_TOOL_SELECTOR = "a:has-text('List a Tool'), button:has-text('List a Tool')"
STACKSHARE_CONTINUE_SELECTOR = "button:has-text('Continue')"
STACKSHARE_SUBMIT_SELECTOR = "[role='dialog'] button:has-text('Submit')"
STACKSHARE_SUBMISSION_SUCCESS_PATTERNS = [
    "thank you",
    "thanks for submitting",
    "submitted",
    "submission received",
    "pending review",
    "we will review",
    "we'll review",
    "your tool has been submitted",
]
STACKSHARE_DEFAULT_SENTINELS = {
    "your",
    "your-site.com website hosting",
    "https://your-site.com/",
}
STACKSHARE_COOLDOWN_PATTERNS = [
    r"please try again in (?P<remaining>\d+)\s*hours?",
    r"try again in (?P<remaining>\d+)\s*hours?",
    r"wait (?P<remaining>\d+)\s*hours?",
    r"you can only list one tool per (?P<window>\d+)\s*hours?",
    r"come back tomorrow",
    r"already submitted",
    r"submitted a tool",
    r"please wait",
    r"cooldown",
]

STACKSHARE_LIST_TOOL_SELECTORS = [STACKSHARE_LIST_TOOL_SELECTOR]
STACKSHARE_CONTINUE_SELECTORS = [STACKSHARE_CONTINUE_SELECTOR]
STACKSHARE_SUBMIT_SELECTORS = [STACKSHARE_SUBMIT_SELECTOR]
