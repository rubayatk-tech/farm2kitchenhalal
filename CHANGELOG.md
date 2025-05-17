# Changelog

All notable changes to this project will be documented in this file.

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