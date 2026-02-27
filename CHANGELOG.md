# Changelog

All notable changes to this project will be documented in this file.

---

## [v2.2.0] – 2026-02-27
### Security — PIN Authentication & Dashboard Privacy

#### Feature: 4-Digit PIN Authentication
- Users must now set a 4-digit numeric PIN when submitting their first order
- Returning users must enter their existing PIN to update their order — incorrect PIN returns a `403` error
- PINs are never stored in plain text — hashed using Werkzeug's `generate_password_hash` (pbkdf2:sha256)
- `pin_hash` column added to `User` model; auto-migrated on startup for existing deployments
- Safety net: if a user record exists with no PIN set (e.g. migrated data), the first submitted PIN is accepted and registered

#### Feature: Dashboard Privacy Redaction
- Public visitors now see redacted identity data on `/dashboard`:
  - **Name**: shown as `****`
  - **Phone**: shown as `******XXXX` (last 4 digits only)
- Logged-in admins continue to see full name and phone number
- No backend changes required — `is_admin` session flag already passed to template

#### Pre-deploy Note
- Existing test user records should be cleared before deploying to production (no PIN hashes on old rows)

---

## [v2.1.1] – 2026-02-27
### Pre-flight Fixes (ahead of v2.2 security work)

#### Dependencies
- Removed unused `qrcode==7.4.2` and `Pillow==10.4.0` from requirements (never imported)
- Pinned `psycopg2-binary==2.9.11` (was unpinned, risking incompatible installs)

#### Bug Fixes
- Fixed `shared_cost` input causing HTTP 500 on non-numeric values — now silently defaults to `0.0`
- Replaced bare `except:` in `edit_order` quantity parsing with `except (ValueError, IndexError):`
- Replaced bare `except:` in `update_payment` float conversion with `except (ValueError, TypeError):`

#### Security
- Fixed open redirect: `?next=` parameter in `/confirm_order` and `/delete_order` now validated to be a local path only (must start with `/`, not `//`)

---

## [v2.1.0] – 2026-02-26
### Dynamic Pricing & Price Snapshot Protection

#### New Features
- Prices are now stored in the database (`ItemPrice` table) and editable by admin from the dashboard — no redeployment needed
- Admin dashboard includes a new "Manage Prices" section with live price editing per item
- Each order now stores a `price_snapshot` (JSON) capturing the exact prices at submission time
- Editing an existing order uses the locked snapshot prices, not current prices — protecting customers from retroactive rate changes
- On first startup, `ItemPrice` table is auto-seeded from `config.py` defaults
- Existing deployments are migrated automatically: `price_snapshot` column added to `order` table on startup if missing

#### How It Works
- New orders: prices fetched from DB → total calculated → snapshot stored with order
- Price update: admin changes prices in dashboard → only affects future orders
- Order edit: quantities can be changed but rates stay locked to original snapshot

---

## [v2.0.0] – 2026-02-26
### Production Readiness & Code Cleanup

#### Deployment Fixes
- Added `gunicorn==21.2.0` to `requirements.txt` for production WSGI serving
- Added `Procfile` with `web: gunicorn app:app` for Render.com deployment
- Moved `SECRET_KEY` from hardcoded value to environment variable (raises `ValueError` if unset)
- Set `debug=False` in `app.run()` to prevent Werkzeug debugger exposure in production

#### Code Quality
- Removed duplicate `from fractions import Fraction` import (was imported twice)
- Removed unused `import re`
- Removed dead `is_valid_goat_total()` helper function (defined but never called)
- Replaced deprecated `Order.query.get_or_404()` with `db.get_or_404(Order, id)` across all 4 routes

---

## [v1.4.2] – 2025-05-17
### 💳 Payment Tracking & Admin Enhancements
Added new amount_paid field to each order (schema updated in production)

Introduced "Amount Paid" and "Remaining Due" columns to the dashboard

Remaining Due is color-coded:

🔴 Red = balance due

🟢 Green = overpayment (if any)

⚪️ Gray = exact payment

Added inline admin form to record payments per customer

New summary card displays Total Amount Received

All changes are backward-compatible — existing orders remain untouched

Note: This version includes only backend and dashboard logic updates. Pricing changes, if needed, will be included in a future release.

## [v1.4.1] – 2025-05-14
### 🔧 Feature Enhancement: Cow Sizes Split Ordering
Replaced single "Cow (1/7) Share" option with:

🐄 Cow Size 1 (Large) – 1/7 share of a $4000 cow

🐄 Cow Size 2 (Small) – 1/7 share of a $2000 cow

Updated pricing logic to reflect per-share cost of each cow size

Updated order form UI to support both cow sizes with separate selection

Cleaned up legacy cattle tagging logic for simplicity and future flexibility

Deployed new PostgreSQL-backed database for long-term durability

Reset order history for cleaner tracking under new pricing model

Note: All prior orders have been cleared as part of the migration. Customers are kindly asked to resubmit using the new form.

## [v1.4.0] – 2025-05-14

### ✨ Qurbani-Only Seasonal Release
- Replaced traditional menu with Qurbani-specific options:
  - Cow (1/7) Share
  - Full Goat
  - Full Sheep
  - Full Lamb
- Repurposed the regular order form as a Qurbani Order Form
- Cleaned all previous poultry/egg-based items and routes
- Admin Dashboard:
  - View, Edit, Confirm, and Delete Qurbani orders
  - Apply shared cost across confirmed orders
  - Export confirmed orders to PDF
- Login-protected admin panel with support for multiple phone numbers
- General code cleanup and route simplification for seasonal focus

> **Note**: This release deprecates regular ordering features. Use v1.3.0 tag to restore previous menu.

## [v1.3.0] – 2025-05-08

### ✨ Features
- Added `/qurbani_order` route with dropdown-based Qurbani order form (Cow, Goat, Sheep, Lamb)
- Introduced `/qurbani_dashboard` with admin-only controls (Confirm, Edit, Delete)
- Added PDF export for confirmed Qurbani orders (`/export_qurbani_confirmed_pdf`)
- New model field `source` added to distinguish regular vs Qurbani orders
- Admin login page restyled and branded as "Farm2Kitchen Admin Login"
- Main `/dashboard` now includes Shared Cost and Total Due columns
- Shared Cost is applied equally to confirmed regular orders
- Restored "Clear All Orders" functionality (excludes Qurbani orders)
- Added prominent "Qurbani Order" button on homepage (seasonal promotion)

### 🛠 Fixes & Improvements
- `/confirm_order`, `/delete_order` now support `?next=` to preserve origin dashboard
- `/dashboard` and `/export_confirmed_pdf` now only show regular orders
- `/qurbani_dashboard` fully filtered by `source='qurbani'`
- Fixed goat price calculation by using `goat_full` instead of `goat (per lb)`

---

## [v1.2.2] – 2025-05-06
- Feature: Adding Qurbani Route

---

## [v1.2.1] – 2025-05-06
- Feature: (Goat dropdown Menu) 

---

## [v1.2.0] – 2025-05-06
### Added
- Admin can delete orders (`feature/admin-delete-order`)
- Export confirmed orders to PDF with styled table (`feature/pdf-export-confirmed-orders`)

---

## [v1.1.0] – 2025-05-05
### Added
- Admin can edit submitted orders via structured form
- Real-time calculation on edit page
- Shared cost dynamically shown on dashboard

---

## [v1.0.0] – 2025-05-04
### Initial MVP
- Order form with validation
- Dashboard with order listing
- Admin login with environment variable protection
- SQLite-backed order storage