import os

PRICES = {
    # 🐄 Qurbani-specific
    "cow_share_large": float(os.getenv("PRICE_COW_LARGE", 571.43)),  # 1/7th of $4000
    "cow_share_small": float(os.getenv("PRICE_COW_SMALL", 285.71)),  # 1/7th of $2000
    "goat_full": float(os.getenv("PRICE_GOAT_FULL", 450.0)),
    "sheep": float(os.getenv("PRICE_SHEEP", 350.0)),
    "lamb": float(os.getenv("PRICE_LAMB", 350.0))
}

LABELS = {
    # 🐄 Qurbani labels
    "cow_share_large": "Cow Size 1 (Large) - 1/7 Share",
    "cow_share_small": "Cow Size 2 (Small) - 1/7 Share",
    "goat_full": "Full Goat",
    "sheep": "Full Sheep",
    "lamb": "Full Lamb"
}

ALLOWED_ADMINS = os.getenv("ADMIN_PHONES", "").split(",")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable is not set.")
