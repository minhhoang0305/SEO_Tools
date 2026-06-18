KYI_AI_SUBMIT_URL = "https://kyi.ai/submit"

KYI_AI_SUCCESS_PATTERNS = (
    "success",
    "submitted",
    "thank you",
    "thanks",
    "received",
    "successfully",
)

KYI_AI_POPUP_SELECTORS = (
    "[data-sonner-toast][data-type='success']",
    "[role='status'][data-type='success']",
    "li[data-sonner-toast][data-type='success']",
    "[data-sonner-toast]",
    "[role='dialog']",
    ".modal",
    ".modal-dialog",
    ".toast",
    ".swal2-popup",
    ".swal2-container",
    ".ant-modal",
    ".MuiDialog-root",
    ".popup",
)
