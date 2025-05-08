# 🔹 1. Standard Library
import os
from io import BytesIO
from datetime import timedelta

# 🔹 2. Environment Variables
from dotenv import load_dotenv
load_dotenv()

# 🔹 3. Utility Libraries
from fractions import Fraction
import re

# 🔹 4. Flask Core and Extensions
from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy

# 🔹 5. PDF ReportLab Libraries
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# App configuration
from config import PRICES, LABELS, ALLOWED_ADMINS, ADMIN_PASSWORD


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

app.permanent_session_lifetime = timedelta(minutes=30)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zelle_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items_ordered = db.Column(db.String(500), nullable=False)
    total_price_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    source = db.Column(db.String(20), default='regular')
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    #goat_share = db.Column(db.String(10))  # e.g., '1/3', '1/2', '1'

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.Float)

# Helper Function 
def is_valid_goat_total(pending_share="0", include_current=True):
    total = Fraction(0)

    # This now gets all orders, not just confirmed ones
    orders = Order.query.all()

    for order in orders:
        if order.status == 'Confirmed' or include_current:
            matches = re.findall(r"Goat:\s*([\d/]+)", order.items_ordered)
            for match in matches:
                try:
                    total += Fraction(match.strip())
                except:
                    continue

    try:
        total += Fraction(pending_share.strip())
    except:
        pass

    return total.denominator == 1

# Main Landing Page 
@app.route('/')
def index():
    return render_template('index.html', prices=PRICES, labels=LABELS)

# Dashboard Route 
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST' and session.get('admin'):
        shared_cost = float(request.form.get('shared_cost', 0))
        config = Config.query.filter_by(key='shared_cost').first()
        if not config:
            config = Config(key='shared_cost', value=shared_cost)
            db.session.add(config)
        else:
            config.value = shared_cost
        db.session.commit()
        return redirect('/dashboard')

    orders = Order.query.all()
    shared_cost_cfg = Config.query.filter_by(key='shared_cost').first()
    shared_cost = shared_cost_cfg.value if shared_cost_cfg else 0
    num_orders = len(orders)
    shared_per_order = (shared_cost / num_orders) if num_orders else 0
    return render_template('dashboard.html', orders=orders, shared_per_order=shared_per_order, is_admin=session.get('admin', False))

# Submitting an Order Route 
@app.route('/submit_order', methods=['POST'])
def submit_order():
    zelle_name = request.form.get('zelle_name')
    phone = request.form.get('phone')

    # 🔐 Validate phone number
    if not phone.isdigit() or len(phone) != 10:
        return "Phone number must be exactly 10 digits.", 400

    items_ordered = []
    total = 0.0

    for key, price in PRICES.items():
        val = request.form.get(key)
        if val:
            try:
                # Handle goat share using Fraction
                if key == 'goat':
                    share = float(Fraction(val))
                    if share > 0:
                        total += share * price
                        items_ordered.append(f"Goat: {val}")
                else:
                    quantity = float(val)
                    if quantity > 0:
                        label = LABELS.get(key, key)
                        total += quantity * price
                        items_ordered.append(f"{label}: {int(quantity) if quantity.is_integer() else quantity}")
            except (ValueError, ZeroDivisionError):
                continue  # Ignore invalid values

    items_str = ', '.join(items_ordered) if items_ordered else "No items"

    # Get or create the user
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(zelle_name=zelle_name, phone=phone)
        db.session.add(user)
        db.session.commit()

    # Create or update the order
    existing_order = Order.query.filter_by(user_id=user.id).first()
    if existing_order:
        existing_order.items_ordered = items_str
        existing_order.total_price_usd = total
    else:
        new_order = Order(user_id=user.id, items_ordered=items_str, total_price_usd=total)
        db.session.add(new_order)

    db.session.commit()
    return redirect('/dashboard')


# Admin User Login  
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    session.permanent = True
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        if phone in ALLOWED_ADMINS and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/dashboard')
        else:
            return "Access denied", 403
    return render_template('admin_login.html')

# Admin User confirming order   

@app.route('/confirm_order/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403

    order = Order.query.get_or_404(order_id)

    # ✅ Skip goat share validation
    order.status = 'Confirmed'
    db.session.commit()
    return redirect('/dashboard')

# Admin User Logging Out   
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/dashboard')

# Admin User Clearing all the orders
@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if not session.get('admin'):
        return "Unauthorized", 403
    Order.query.delete()
    db.session.commit()
    return redirect('/dashboard')


@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403

    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        quantities = {}
        total_price = 0.0
        for key in PRICES:
            qty = float(request.form.get(key, 0) or 0)
            if qty > 0:
                quantities[key] = qty
                total_price += qty * PRICES[key]

        # Rebuild items_ordered string
        items_ordered = ', '.join([f"{LABELS[key]}: {int(quantities[key])}" for key in quantities])
        order.items_ordered = items_ordered
        order.total_price_usd = total_price
        db.session.commit()
        return redirect('/dashboard')

    # Extract current order into item: quantity dict
    quantities = {}
    for key in PRICES:
        label = LABELS[key]
        if label in order.items_ordered:
            try:
                part = order.items_ordered.split(label + ":")[1].split(",")[0].strip()
                quantities[key] = int(part)
            except:
                quantities[key] = 0
        else:
            quantities[key] = 0

    return render_template(
        "edit_order.html",
        order=order,
        prices=PRICES,
        labels=LABELS,
        quantities=quantities
    )

@app.route('/export_confirmed_pdf')
def export_confirmed_pdf():
    if not session.get('admin'):
        return "Unauthorized", 403

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Confirmed Orders Summary", styles['Title']))
    elements.append(Spacer(1, 12))

    confirmed_orders = Order.query.filter_by(status="Confirmed").all()

    # Table header
    data = [["Name", "Phone", "Items Ordered", "Total Paid (USD)"]]

    for order in confirmed_orders:
        # Use line breaks for each item
        formatted_items = Paragraph(order.items_ordered.replace(", ", "<br/>"), styles['Normal'])
        data.append([
            order.user.zelle_name,
            order.user.phone,
            formatted_items,
            f"${order.total_price_usd:.2f}"
        ])

    # Create styled table
    table = Table(data, colWidths=[120, 100, 260, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="confirmed_orders.pdf", mimetype='application/pdf')

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(request.args.get('next', '/dashboard'))

@app.route('/qurbani_order')
def qurbani_order():
    return render_template('qurbani.html')

@app.route('/submit_qurbani_order', methods=['POST'])
def submit_qurbani_order():
    zelle_name = request.form.get('zelle_name')
    phone = request.form.get('phone')

    if not phone.isdigit() or len(phone) != 10:
        return "Phone number must be exactly 10 digits.", 400

    items_ordered = []
    total = 0.0

    # Define prices — or pull from config.py if already defined
    qurbani_prices = {
        "cow_share": PRICES.get("cow_share", 0),
        "goat_full": PRICES.get("goat", 0),
        "sheep": PRICES.get("sheep", 0),
        "lamb": PRICES.get("lamb", 0),
    }

    for key in qurbani_prices:
        val = request.form.get(key)
        if val and float(val) > 0:
            quantity = float(val)
            total += quantity * qurbani_prices[key]
            label = key.replace("_", " ").title()
            items_ordered.append(f"{label}: {int(quantity) if quantity.is_integer() else quantity}")

    items_str = ', '.join(items_ordered) if items_ordered else "No items"

    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(zelle_name=zelle_name, phone=phone)
        db.session.add(user)
        db.session.commit()

    new_order = Order(user_id=user.id, items_ordered=items_str, total_price_usd=total, status="Pending", source="qurbani")
    db.session.add(new_order)
    db.session.commit()

    return redirect('/qurbani_dashboard')

@app.route('/qurbani_dashboard')
def qurbani_dashboard():
    keywords = ["Cow", "Goat", "Sheep", "Lamb"]
    all_orders = Order.query.all()
    qurbani_orders = [
        order for order in all_orders
        if any(word in order.items_ordered for word in keywords)
    ]
    return render_template('qurbani_dashboard.html', orders=qurbani_orders, is_admin=session.get('admin', False))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))  # 🔁 Render sets this env variable
    app.run(host='0.0.0.0', port=port, debug=True)



