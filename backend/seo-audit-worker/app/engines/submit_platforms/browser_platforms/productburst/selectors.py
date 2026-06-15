from __future__ import annotations

# Auth
PRODUCTBURST_GOOGLE_LOGIN_SELECTORS = [
    "button:has-text('Continue with Google')",
    "button:has-text('Google')",
    "a:has-text('Continue with Google')",
]

PRODUCTBURST_EMAIL_INPUT_SELECTORS = [
    "input[type='email']",
    "input[placeholder*='Email']",
    "input[name='email']",
]

PRODUCTBURST_PASSWORD_INPUT_SELECTORS = [
    "input[type='password']",
    "input[placeholder*='Password']",
    "input[name='password']",
]

PRODUCTBURST_SIGNIN_SELECTORS = [
    "button:has-text('Sign in')",
    "button:has-text('Login')",
    "button[type='submit']",
]

PRODUCTBURST_AUTH_FORM_SELECTORS = [
    *PRODUCTBURST_EMAIL_INPUT_SELECTORS,
    *PRODUCTBURST_PASSWORD_INPUT_SELECTORS,
]

# Launch / pre-launch page
PRODUCTBURST_STARTUP_NAME_SELECTORS = [
    "input[placeholder*='Startup Name']",
    "input[name='startupName']",
    "input[name='name']",
]

PRODUCTBURST_LIVE_WEBSITE_SELECTORS = [
    "input[placeholder*='Live Website Link']",
    "input[placeholder*='website.com']",
    "input[name='url']",
    "input[name='website']",
    "input[type='url']",
]

PRODUCTBURST_TAGLINE_SELECTORS = [
    "input[placeholder*='Tagline']",
    "input[name='tagline']",
]

PRODUCTBURST_DESCRIPTION_SELECTORS = [
    "textarea[placeholder*='Product description']",
    "textarea[placeholder*='description']",
    "div[contenteditable='true']",
]

PRODUCTBURST_CATEGORY_SELECTORS = [
    "input[placeholder*='Choose some options']",
    "input[placeholder*='Choose Category']",
    "input[name='categories']",
]

PRODUCTBURST_STACK_SELECTORS = [
    "input[placeholder*='Choose some options']",
    "input[placeholder*='Select Stack']",
    "input[name='stacks']",
]

PRODUCTBURST_PRODUCT_TYPE_SELECTORS = [
    "select[name='productType']",
    "select[name='type']",
    "select",
]

PRODUCTBURST_LAUNCH_WEEK_SELECTORS = [
    "input[name='launchWeek']",
    "select[name='launchWeek']",
]

PRODUCTBURST_LOGO_UPLOAD_SELECTORS = [
    "input[type='file']",
]

PRODUCTBURST_PREVIEW_TOGGLE_SELECTORS = [
    "button[role='switch']",
    "input[type='checkbox']",
]

PRODUCTBURST_CREATORS_SEARCH_SELECTORS = [
    "input[placeholder*='Search for creators']",
    "input[placeholder*='creators']",
    "input[name='creators']",
]

PRODUCTBURST_FIRST_COMMENT_SELECTORS = [
    "input[type='checkbox']",
    "button:has-text('Create First Comment')",
]

PRODUCTBURST_LAUNCH_BUTTON_SELECTORS = [
    "button:has-text('Launch')",
    "button:has-text('Schedule')",
    "button:has-text('Publish')",
]

