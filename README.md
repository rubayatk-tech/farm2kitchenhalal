# Farm2Kitchen Halal — Ordering App

**v2.2.0** — A lightweight community ordering app for a local halal meat and egg operation. Customers submit orders via a simple web form; admins manage everything from a secure dashboard.

---

## Features

**Customer-facing**
- Submit orders for beef, goat, poultry, duck, quail, and eggs
- 4-digit PIN authentication — set on first order, required to update
- Price breakdown shown at submission time; prices are locked to the snapshot at order time

**Admin dashboard**
- Secure login with phone number and password (30-minute session)
- View, confirm, edit, and delete orders
- Privacy redaction: public view masks names and phone numbers; admins see full data
- Shared delivery/tip cost split across all orders
- Payment tracking (amount paid per order)
- Dynamic price management — update item prices from the dashboard without redeployment
- Export confirmed orders as a PDF summary

---

## Item Catalogue

| Item | Unit | Default Price |
|------|------|--------------|
| Cow / Beef | lb | $6.00 |
| Goat | lb | $10.00 |
| Desi Hard Chicken — Skin-OFF (1–2 lbs) | each | $9.00 |
| Desi Hard Chicken — Skin-ON (1–2 lbs) | each | $8.00 |
| Young Hen / Poulette (3–4 lbs) | each | $17.00 |
| Rooster (4–5 lbs) | each | $17.00 |
| Broiler (8–9 lbs) | each | $15.00 |
| Young Peking Duck (6 lbs & up) | each | $20.00 |
| Quail | each | $5.00 |
| Chicken Eggs | dozen | $5.00 |

Prices are managed via the admin dashboard and stored in the database (`ItemPrice` table). Defaults can be overridden at startup via `PRICE_*` environment variables.

---

## Tech Stack

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.9.6 | Virtual environment (`venv/`) |
| Flask | 2.3.3 | Core web framework |
| Werkzeug | 2.3.8 | WSGI toolkit; PIN/password hashing via `pbkdf2:sha256` |
| Flask-SQLAlchemy | 3.0.5 | ORM extension |
| SQLAlchemy | 2.0.40 | Database ORM |
| Jinja2 | 3.1.6 | HTML templating |
| python-dotenv | 1.0.1 | `.env` file loading |
| ReportLab | 4.0.7 | PDF export |
| psycopg2-binary | 2.9.11 | PostgreSQL adapter (production) |
| gunicorn | 21.2.0 | WSGI server (production / Render) |
| SQLite | 3.43.2 | Local development database |

---

## Environment Variables

Create a `.env` file in the project root for local development:

```env
SECRET_KEY=your-secret-key
ADMIN_PHONES=1234567890,0987654321
ADMIN_PASSWORD=your-admin-password

# Optional: override default item prices at startup
PRICE_COW_BEEF=6.0
PRICE_GOAT=10.0
PRICE_DESI_CHICKEN_SKIN_OFF=9.0
PRICE_DESI_CHICKEN_SKIN_ON=8.0
PRICE_YOUNG_HEN=17.0
PRICE_ROOSTER=17.0
PRICE_BROILER=15.0
PRICE_DUCK=20.0
PRICE_QUAIL=5.0
PRICE_EGGS=5.0
```

In production (Render), set these as environment variables in the service dashboard. `DATABASE_URL` is set automatically by Render's PostgreSQL add-on.

---

## Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/farm2kitchenhalal.git
cd farm2kitchenhalal
```

### 2. Create and activate a virtual environment
```bash
python3.9 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env   # or create .env manually (see above)
```

### 5. Run the app
```bash
python app.py
```

### 6. Access the app
- Customer order form: `http://127.0.0.1:5000`
- Admin dashboard: `http://127.0.0.1:5000/dashboard`

The app auto-creates the SQLite database and seeds item prices on first run.

---

## Project Structure

```
farm2kitchenhalal/
│
├── app.py                  # All routes, DB models, startup migrations
├── config.py               # PRICES, LABELS, UNITS, ALLOWED_ADMINS, ADMIN_PASSWORD
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html          # Customer order form
│   ├── dashboard.html      # Admin dashboard
│   ├── edit_order.html     # Admin order editor
│   └── admin_login.html    # Admin login page
├── instance/               # Local SQLite DB files (git-ignored)
└── README.md
```

---

## Deployment (Render)

The app is configured for deployment on [Render](https://render.com):

- **Runtime**: Python, Gunicorn WSGI server
- **Database**: Render PostgreSQL (connection string injected as `DATABASE_URL`)
- **Start command**: `gunicorn app:app`
- On startup, the app runs `db.create_all()` and auto-migrates any missing columns, so redeployment is non-destructive

---

## Changelog

| Version | Summary |
|---------|---------|
| v2.2.0 | PIN authentication for customers; dashboard privacy redaction; security fixes |
| v2.1.0 | Dynamic pricing via DB; per-order price snapshots; new poultry/farm item catalogue |
| v2.0.0 | Production readiness; PostgreSQL support; Render deployment |
| v1.4.2 | Amount paid tracking and payment summary |
| v1.4.1 | Cow size split ordering; separate DB |
