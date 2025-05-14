import os

PRICES = {
    # 🐄 Qurbani-specific
    "cow_share": float(os.getenv("PRICE_COW_SHARE", 525.0)),
    "goat_full": float(os.getenv("PRICE_GOAT_FULL", 450.0)),  # 🐐 full goat
    "sheep": float(os.getenv("PRICE_SHEEP", 350.0)),
    "lamb": float(os.getenv("PRICE_LAMB", 350.0))


}

LABELS = {

    # 🐄 Qurbani labels
    "cow_share": "Cow (1/7) Share",
    "goat_full": "Full Goat",
    "sheep": "Full Sheep",
    "lamb": "Full Lamb"

}

ALLOWED_ADMINS = os.getenv("ADMIN_PHONES", "").split(",")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable is not set.")
