from __future__ import annotations

AWESOME_INDY_BASE_URL = "https://awesomeindie.com"
AWESOME_INDY_HOME_URL = AWESOME_INDY_BASE_URL
AWESOME_INDY_SUBMIT_URL = f"{AWESOME_INDY_BASE_URL}/submit"
AWESOME_INDY_CATEGORIES_URL = f"{AWESOME_INDY_BASE_URL}/api/categories/get-categories"
AWESOME_INDY_POST_PRODUCT_URL = f"{AWESOME_INDY_BASE_URL}/api/products/post-product"
AWESOME_INDY_MY_PRODUCTS_URL = f"{AWESOME_INDY_BASE_URL}/api/products/get-my-products"

AWESOME_INDY_SUCCESS_PATTERNS = (
    "success",
    "submitted",
    "created",
    "added",
    "thank you",
    "thanks",
    "saved",
)

AWESOME_INDY_SUCCESS_SELECTORS = (
    "[data-sonner-toast][data-type='success']",
    "[role='status'][data-type='success']",
    "li[data-sonner-toast][data-type='success']",
    "[data-sonner-toast]",
    "[role='alert']",
    ".toast",
    ".swal2-popup",
    ".swal2-container",
    ".modal",
    ".popup",
)

