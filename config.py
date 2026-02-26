import os

PRICES = {
    "cow_beef":               float(os.getenv("PRICE_COW_BEEF", 6.0)),
    "goat":                   float(os.getenv("PRICE_GOAT", 10.0)),
    "desi_chicken_skin_off":  float(os.getenv("PRICE_DESI_CHICKEN_SKIN_OFF", 9.0)),
    "desi_chicken_skin_on":   float(os.getenv("PRICE_DESI_CHICKEN_SKIN_ON", 8.0)),
    "young_hen":              float(os.getenv("PRICE_YOUNG_HEN", 17.0)),
    "rooster":                float(os.getenv("PRICE_ROOSTER", 17.0)),
    "broiler":                float(os.getenv("PRICE_BROILER", 15.0)),
    "duck":                   float(os.getenv("PRICE_DUCK", 20.0)),
    "quail":                  float(os.getenv("PRICE_QUAIL", 5.0)),
    "eggs":                   float(os.getenv("PRICE_EGGS", 5.0)),
}

LABELS = {
    "cow_beef":               "🐄 Cow/Beef",
    "goat":                   "🐐 Goat",
    "desi_chicken_skin_off":  "🐓 Desi Hard Chicken (1–2 lbs) (Skin-OFF)",
    "desi_chicken_skin_on":   "🐓 Desi Hard Chicken (1–2 lbs) (Skin-ON)",
    "young_hen":              "🐔 Young Hen / Poulette (3–4 lbs)",
    "rooster":                "🐓 Rooster (4–5 lbs)",
    "broiler":                "🐥 Broiler (8–9 lbs)",
    "duck":                   "🦆 Young Peaking Duck (6 lbs & up)",
    "quail":                  "🕊️ Quail",
    "eggs":                   "🍳 Chicken Eggs",
}

UNITS = {
    "cow_beef":               "lb",
    "goat":                   "lb",
    "desi_chicken_skin_off":  "each",
    "desi_chicken_skin_on":   "each",
    "young_hen":              "each",
    "rooster":                "each",
    "broiler":                "each",
    "duck":                   "each",
    "quail":                  "each",
    "eggs":                   "dozen",
}

ALLOWED_ADMINS = os.getenv("ADMIN_PHONES", "").split(",")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable is not set.")
