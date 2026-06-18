from __future__ import annotations

NEWAIFORYOU_ADD_PRODUCT_SELECTORS = [
    "button:has-text('AddProduct')",
    "button:has-text('Add Product')",
    "a:has-text('AddProduct')",
    "a:has-text('Add Product')",
    "button:has-text('Submit')",
]

NEWAIFORYOU_TOOL_NAME_SELECTORS = [
    "input[name='toolname']",
    "input[name='tool_name']",
    "input[name='toolName']",
    "input[placeholder*='Tool name']",
    "input[placeholder*='tool name']",
    "input[placeholder*='Name']",
]

NEWAIFORYOU_URL_SELECTORS = [
    "input[name='url']",
    "input[name='website_url']",
    "input[name='websiteUrl']",
    "input[type='url']",
    "input[placeholder*='URL']",
    "input[placeholder*='url']",
]

NEWAIFORYOU_SUBMIT_BUTTON_SELECTORS = [
    "button[type='submit']",
    "button:has-text('Submit')",
    "button:has-text('Submit product')",
    "button:has-text('Submit Product')",
    "input[type='submit']",
]
