import os

PRICES = {
    "cow": float(os.getenv("PRICE_COW", 4.5)),
    "goat": float(os.getenv("PRICE_GOAT", 9.0)),
    "dh_off": float(os.getenv("PRICE_DH_OFF", 9.0)),
    "dh_on": float(os.getenv("PRICE_DH_ON", 8.0)),
    "yh": float(os.getenv("PRICE_YH", 17.0)),
    "r": float(os.getenv("PRICE_R", 17.0)),
    "b": float(os.getenv("PRICE_B", 15.0)),
    "duck": float(os.getenv("PRICE_DUCK", 20.0)),
    "quail": float(os.getenv("PRICE_QUAIL", 6.0)),
    "turkey": float(os.getenv("PRICE_TURKEY", 70.0)),
    "egg": float(os.getenv("PRICE_EGG", 6.0)),

    # 🐄 Qurbani-specific
    "cow_share": float(os.getenv("PRICE_COW_SHARE", 350.0)),
    "goat_full": float(os.getenv("PRICE_GOAT_FULL", 280.0)),  # 🐐 full goat
    "sheep": float(os.getenv("PRICE_SHEEP", 260.0)),
    "lamb": float(os.getenv("PRICE_LAMB", 300.0))


}

LABELS = {
    "cow": "Cow (lbs)",
    "goat": "Goat Share (lbs)",
    "dh_off": "Desi Hard (Skin OFF)",
    "dh_on": "Desi Hard (Skin ON)",
    "yh": "Young Hen",
    "r": "Rooster",
    "b": "Broiler",
    "duck": "Duck",
    "quail": "Quail",
    "turkey": "Turkey",
    "egg": "Egg (Dozen)",

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
