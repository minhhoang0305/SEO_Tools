from __future__ import annotations

AWESOME_INDY_ADD_PRODUCT_SELECTORS = [
    "button:has-text('AddProduct')",
    "button:has-text('Add Product')",
    "a:has-text('AddProduct')",
    "a:has-text('Add Product')",
    "text=AddProduct",
    "text=Add Product",
]

AWESOME_INDY_PRODUCT_NAME_SELECTORS = [
    "input[name='product_name']",
    "input[name='productName']",
    "input[name='name']",
    "input[placeholder*='Product name']",
    "input[placeholder*='Name']",
]

AWESOME_INDY_URL_SELECTORS = [
    "input[name='url']",
    "input[name='website_url']",
    "input[name='websiteUrl']",
    "input[type='url']",
    "input[placeholder*='URL']",
]

AWESOME_INDY_TAGLINE_SELECTORS = [
    "input[name='tagline']",
    "textarea[name='tagline']",
    "input[placeholder*='Tagline']",
    "textarea[placeholder*='Tagline']",
]

AWESOME_INDY_CATEGORIES_SELECTORS = [
    "select[name='categories']",
    "select[name='category']",
    "input[name='categories']",
    "input[placeholder*='Categories']",
    "input[placeholder*='Category']",
    "[role='combobox']",
]

AWESOME_INDY_DESCRIPTION_SELECTORS = [
    "textarea[name='description']",
    "textarea[name='productDescription']",
    "textarea[placeholder*='Description']",
    "div[contenteditable='true']",
]

AWESOME_INDY_SOCIAL_LINKS_SELECTORS = [
    "textarea[name='socialLinks']",
    "input[name='socialLinks']",
    "input[placeholder*='Social links']",
    "textarea[placeholder*='Social links']",
]

AWESOME_INDY_YOUTUBE_SELECTORS = [
    "input[name='youtubeVideoUrl']",
    "input[name='youtube_video_url']",
    "input[name='youtube']",
    "input[placeholder*='YouTube video URL']",
    "input[placeholder*='YouTube']",
]

AWESOME_INDY_SUBMIT_BUTTON_SELECTORS = [
    "button[type='submit']",
    "button:has-text('Submit product')",
    "button:has-text('Submit')",
    "button:has-text('Post Product')",
    "button:has-text('Submit Product')",
    "input[type='submit']",
]
