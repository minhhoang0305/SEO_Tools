from __future__ import annotations

NEWAIFORYOU_BASE_URL = "https://newaiforyou.com"
NEWAIFORYOU_HOME_URL = NEWAIFORYOU_BASE_URL
NEWAIFORYOU_SUBMIT_URL = f"{NEWAIFORYOU_BASE_URL}/submit"
NEWAIFORYOU_POST_PRODUCT_URL = f"{NEWAIFORYOU_BASE_URL}/api/products/post-product"

NEWAIFORYOU_SUCCESS_PATTERNS = (
    "success",
    "submitted",
    "created",
    "thank you",
    "thanks",
    "saved",
    "done",
)

NEWAIFORYOU_MODAL_SELECTORS = (
    "[role='dialog']",
    "[role='alertdialog']",
    ".ant-modal",
    ".ant-modal-content",
    ".ant-modal-confirm",
    ".modal",
    ".popup",
)

NEWAIFORYOU_SUCCESS_SELECTORS = (
    "[data-sonner-toast][data-type='success']",
    "[role='status'][data-type='success']",
    "li[data-sonner-toast][data-type='success']",
    "[data-sonner-toast]",
)
