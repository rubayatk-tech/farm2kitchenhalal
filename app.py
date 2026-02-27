# 🔹 1. Standard Library
import os
import json
from io import BytesIO
from datetime import timedelta

# 🔹 2. Environment Variables
from dotenv import load_dotenv
load_dotenv()

# 🔹 3. Flask Core and Extensions
from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 🔹 4. PDF ReportLab Libraries
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# App configuration
from config import PRICES, LABELS, UNITS, ALLOWED_ADMINS, ADMIN_PASSWORD


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise ValueError("SECRET_KEY environment variable is not set.")
db = SQLAlchemy(app)

app.permanent_session_lifetime = timedelta(minutes=30)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zelle_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    pin_hash = db.Column(db.String(256), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items_ordered = db.Column(db.String(500), nullable=False)
    total_price_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    source = db.Column(db.String(20), default='regular')
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    amount_paid = db.Column(db.Float, default=0.0)
    price_snapshot = db.Column(db.Text, nullable=True)  # JSON: prices at time of order

class ItemPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.Float)


def get_current_prices():
    """Return prices from DB, falling back to config.py defaults for any missing keys."""
    db_prices = {p.key: p.price for p in ItemPrice.query.all()}
    return {key: db_prices.get(key, PRICES[key]) for key in PRICES}


# Main Landing Page
@app.route('/')
def index():
    current_prices = get_current_prices()
    return render_template('index.html', prices=current_prices, labels=LABELS, units=UNITS)

# Dashboard Route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST' and session.get('admin'):
        try:
            shared_cost = float(request.form.get('shared_cost', 0))
        except (ValueError, TypeError):
            shared_cost = 0.0
        config = Config.query.filter_by(key='shared_cost').first()
        if not config:
            config = Config(key='shared_cost', value=shared_cost)
            db.session.add(config)
        else:
            config.value = shared_cost
        db.session.commit()
        return redirect('/dashboard')

    orders = Order.query.filter_by(source="regular").all()
    shared_cost_cfg = Config.query.filter_by(key='shared_cost').first()
    shared_cost = shared_cost_cfg.value if shared_cost_cfg else 0
    num_orders = len(orders)
    shared_per_order = (shared_cost / num_orders) if num_orders else 0
    total_received = sum(order.amount_paid or 0.0 for order in orders)
    current_prices = get_current_prices()
    return render_template(
        'dashboard.html',
        orders=orders,
        shared_per_order=shared_per_order,
        is_admin=session.get('admin', False),
        total_received=total_received,
        current_prices=current_prices,
        labels=LABELS,
        units=UNITS
    )

@app.route('/submit_order', methods=['POST'])
def submit_order():
    zelle_name = request.form.get('zelle_name')
    phone = request.form.get('phone')
    pin = request.form.get('pin', '').strip()

    if not phone.isdigit() or len(phone) != 10:
        return "Phone number must be exactly 10 digits.", 400

    if not pin.isdigit() or len(pin) != 4:
        return "PIN must be exactly 4 digits.", 400

    current_prices = get_current_prices()
    items_ordered = []
    total = 0.0

    for key, price in current_prices.items():
        val = request.form.get(key)
        if val:
            try:
                quantity = float(val)
                if quantity > 0:
                    label = LABELS.get(key, key)
                    unit = UNITS.get(key, "each")
                    total += quantity * price
                    qty_str = int(quantity) if quantity.is_integer() else quantity
                    items_ordered.append(f"{label}: {qty_str} {unit}")
            except (ValueError, ZeroDivisionError):
                continue

    items_str = ', '.join(items_ordered) if items_ordered else "No items"
    snapshot = json.dumps(current_prices)

    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(zelle_name=zelle_name, phone=phone, pin_hash=generate_password_hash(pin))
        db.session.add(user)
        db.session.commit()
    else:
        if user.pin_hash is None:
            user.pin_hash = generate_password_hash(pin)
            db.session.commit()
        elif not check_password_hash(user.pin_hash, pin):
            return "Incorrect PIN. Please try again.", 403

    existing_order = Order.query.filter_by(user_id=user.id).first()
    if existing_order:
        existing_order.items_ordered = items_str
        existing_order.total_price_usd = total
        existing_order.price_snapshot = snapshot
    else:
        new_order = Order(
            user_id=user.id,
            items_ordered=items_str,
            total_price_usd=total,
            price_snapshot=snapshot
        )
        db.session.add(new_order)

    db.session.commit()
    return redirect('/dashboard')


### Administrative Features ###
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

# Admin confirming order
@app.route('/confirm_order/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    order = db.get_or_404(Order, order_id)
    order.status = 'Confirmed'
    db.session.commit()
    next_url = request.args.get('next', '/dashboard')
    if not next_url.startswith('/') or next_url.startswith('//'):
        next_url = '/dashboard'
    return redirect(next_url)

# Admin logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/dashboard')

# Admin clearing all orders
@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if not session.get('admin'):
        return "Unauthorized", 403
    Order.query.filter_by(source="regular").delete()
    db.session.commit()
    return redirect('/dashboard')

# Admin editing an order (uses snapshot prices to preserve original rates)
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403

    order = db.get_or_404(Order, order_id)

    # Use snapshot prices if available, else fall back to current prices
    if order.price_snapshot:
        snapshot_prices = json.loads(order.price_snapshot)
    else:
        snapshot_prices = get_current_prices()

    if request.method == 'POST':
        quantities = {}
        total_price = 0.0
        for key in PRICES:
            qty = float(request.form.get(key, 0) or 0)
            if qty > 0:
                quantities[key] = qty
                total_price += qty * snapshot_prices.get(key, PRICES[key])

        items_ordered = ', '.join([
            f"{LABELS[key]}: {int(quantities[key])} {UNITS.get(key, 'each')}"
            for key in quantities
        ])
        order.items_ordered = items_ordered
        order.total_price_usd = total_price
        db.session.commit()
        return redirect('/dashboard')

    # Parse current quantities from stored string
    quantities = {}
    for key in PRICES:
        label = LABELS[key]
        if label in order.items_ordered:
            try:
                part = order.items_ordered.split(label + ":")[1].split(",")[0].strip().split()[0]
                quantities[key] = int(float(part))
            except (ValueError, IndexError):
                quantities[key] = 0
        else:
            quantities[key] = 0

    return render_template(
        "edit_order.html",
        order=order,
        snapshot_prices=snapshot_prices,
        labels=LABELS,
        units=UNITS,
        quantities=quantities
    )

# Admin update prices
@app.route('/update_prices', methods=['POST'])
def update_prices():
    if not session.get('admin'):
        return "Unauthorized", 403
    for key in PRICES:
        new_price = request.form.get(key)
        if new_price:
            try:
                price = float(new_price)
                item = ItemPrice.query.filter_by(key=key).first()
                if item:
                    item.price = price
                else:
                    db.session.add(ItemPrice(key=key, price=price))
            except ValueError:
                continue
    db.session.commit()
    return redirect('/dashboard')

# Admin export confirmed orders as PDF
@app.route('/export_confirmed_pdf')
def export_confirmed_pdf():
    if not session.get('admin'):
        return "Unauthorized", 403

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Confirmed Orders Summary", styles['Title']))
    elements.append(Spacer(1, 12))

    confirmed_orders = Order.query.filter_by(status='Confirmed', source='regular').all()

    data = [["Name", "Phone", "Items Ordered", "Total Paid (excl. Shp Cost)"]]

    for order in confirmed_orders:
        formatted_items = Paragraph(order.items_ordered.replace(", ", "<br/>"), styles['Normal'])
        data.append([
            order.user.zelle_name,
            order.user.phone,
            formatted_items,
            f"${order.total_price_usd:.2f}"
        ])

    table = Table(data, colWidths=[120, 100, 200, 120])
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

# Admin delete order
@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    order = db.get_or_404(Order, order_id)
    db.session.delete(order)
    db.session.commit()
    next_url = request.args.get('next', '/dashboard')
    if not next_url.startswith('/') or next_url.startswith('//'):
        next_url = '/dashboard'
    return redirect(next_url)

# Admin update payment
@app.route('/update_payment/<int:order_id>', methods=['POST'])
def update_payment(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    order = db.get_or_404(Order, order_id)
    new_amount = request.form.get('amount_paid')
    try:
        order.amount_paid = float(new_amount)
        db.session.commit()
    except (ValueError, TypeError):
        pass
    return redirect('/dashboard')


with app.app_context():
    db.create_all()
    # Add price_snapshot column to existing order table if missing
    try:
        db.session.execute(db.text('ALTER TABLE "order" ADD COLUMN price_snapshot TEXT'))
        db.session.commit()
    except Exception:
        db.session.rollback()
    # Add pin_hash column to existing user table if missing
    try:
        db.session.execute(db.text('ALTER TABLE "user" ADD COLUMN pin_hash VARCHAR(256)'))
        db.session.commit()
    except Exception:
        db.session.rollback()
    # Seed ItemPrice from config defaults if table is empty
    if ItemPrice.query.count() == 0:
        for key, price in PRICES.items():
            db.session.add(ItemPrice(key=key, price=price))
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
