STACKSHARE_TOOL_NAME_SELECTORS = [
    "input[placeholder*='Tool Name']",
    "input[name='name']",
    "input[id='tool_name']",
    "input[aria-label*='Name']",
]

STACKSHARE_WEBSITE_URL_SELECTORS = [
    "input[placeholder*='Website URL']",
    "input[type='url']",
    "input[name='website']",
    "input[name='url']",
    "#website-url",
]

STACKSHARE_DOCS_URL_SELECTORS = [
    "input[placeholder*='Docs URL']",
    "input[placeholder*='Documentation']",
    "input[name='docs']",
    "input[name='documentation']",
]

STACKSHARE_DESCRIPTION_SELECTORS = [
    "input[placeholder*='One-line description']",
    "input[placeholder*='Short description']",
    "textarea[placeholder='Short description (2-3 sentences) *']",
    "textarea[placeholder*='Short description']",
    "textarea[placeholder*='description']",
    "textarea[aria-label*='Description']",
]

STACKSHARE_SHORT_DESCRIPTION_SELECTORS = [
    "textarea[placeholder='Short description (2-3 sentences) *']",
    "textarea[placeholder*='Short description']",
    "textarea[placeholder*='description']",
    "textarea[aria-label*='Description']",
]

STACKSHARE_FEATURES_SELECTORS = [
    "input[placeholder*='Features']",
    "textarea[placeholder*='features']",
    "input[name='features']",
    "textarea[name='features']",
]

STACKSHARE_LOGO_SELECTORS = [
    "input[placeholder*='Logo']",
    "input[name='logo']",
    "input[name='logoUrl']",
]

STACKSHARE_WEBSITE_INPUT_SELECTORS = [
    "#website-url",
    "input#website-url",
    "input[type='url']",
]

STACKSHARE_LIST_TOOL_SELECTORS = [
    "a[href*='tool']",
    "a[href*='submit']",
    "a:has-text('Tool')",
]

STACKSHARE_CONTINUE_SELECTORS = [
    "button:has-text('Continue')",
    "button[type='submit']",
]

STACKSHARE_SUBMIT_SELECTORS = [
    "[role='dialog'] button:has-text('Submit')",
    "button:has-text('Submit')",
]
