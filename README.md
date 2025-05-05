
# 🥩 Farm2Kitchen Ordering App

Farm2Kitchen is a lightweight community ordering app designed to help local meat and egg sellers manage weekly orders. It features a clean user-facing order form and a secure admin dashboard to manage submissions, confirm orders, and apply shared delivery costs.

---

## 🚀 Features

- 📝 Submit orders for chicken, duck, turkey, goat, and eggs.
- 🔐 Admin login with phone number and password.
- 📊 Dashboard for viewing, confirming, and clearing orders.
- 💵 Shared delivery/tip cost split per order.
- 📦 Order summary with price breakdown.
- ✅ 10-digit phone validation (backend).

---

## 🛠️ Tech Stack & Versions

| Component         | Version   | Notes                                  |
|------------------|-----------|----------------------------------------|
| Python           | 3.9.6     | Used within virtual environment        |
| pip              | 25.1.1    | Latest version; package manager        |
| Flask            | 2.3.3     | Core web framework                     |
| Werkzeug         | 2.3.8     | Flask dependency (WSGI toolkit)        |
| Flask-SQLAlchemy | 3.0.5     | Flask extension for SQLAlchemy ORM     |
| SQLAlchemy       | 2.0.40    | Database ORM                           |
| Jinja2           | 3.1.6     | HTML templating engine used by Flask   |
| qrcode           | 7.4.2     | Used for generating QR codes           |
| Pillow           | 10.0.0    | Required for qrcode image rendering    |
| Git              | 2.39.5    | Version control                        |
| SQLite           | 3.43.2    | Lightweight SQL database backend       |
| Virtual Env Path | `venv/`   | Activated using `source venv/bin/activate` |

---

## 🧑‍💻 Local Development Setup

Follow the steps below to run this project on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/farm2kitchen.git
cd farm2kitchen
```

### 2. Create and Activate Virtual Environment
```bash
python3.9 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the App Locally
```bash
python app.py
```

### 5. Access the Web Interface
- Open your browser and go to `http://127.0.0.1:5000`
- Use `/dashboard` for admin interface

---

## 📁 Project Structure

```
farm2kitchen/
│
├── app.py             # Main Flask app with routes and DB models
├── config.py          # Static configs for prices, labels, admin settings
├── requirements.txt   # Python dependencies
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── admin_login.html
└── README.md
```

---

## 📌 Notes

- The app uses SQLite by default for simplicity.
- Admin credentials are hardcoded in `config.py` for now (can be improved).
- Deployment-ready for services like [Render](https://render.com) with minor changes.

---

## 🧼 To Do

- [ ] Add QR code confirmation for each order
- [ ] Email/text notification integration
- [ ] Deploy to cloud (Render, Fly.io, etc.)

---
