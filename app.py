# 🔹 1. Standard Library
import os
from io import BytesIO
from datetime import timedelta

# 🔹 2. Environment Variables
from dotenv import load_dotenv
load_dotenv()

# 🔹 3. Flask Core and Extensions
from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy

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

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items_ordered = db.Column(db.String(500), nullable=False)
    total_price_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    source = db.Column(db.String(20), default='regular')
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    amount_paid = db.Column(db.Float, default=0.0)
    #cattle_tag = db.Column(db.String(5), nullable=True)
    #goat_share = db.Column(db.String(10))  # e.g., '1/3', '1/2', '1'

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.Float)

# Main Landing Page
@app.route('/')
def index():
    return render_template('index.html', prices=PRICES, labels=LABELS, units=UNITS)

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

    orders = Order.query.filter_by(source="regular").all()
    shared_cost_cfg = Config.query.filter_by(key='shared_cost').first()
    shared_cost = shared_cost_cfg.value if shared_cost_cfg else 0
    num_orders = len(orders)
    shared_per_order = (shared_cost / num_orders) if num_orders else 0
    total_received = sum(order.amount_paid or 0.0 for order in orders)
    return render_template('dashboard.html', orders=orders, shared_per_order=shared_per_order, is_admin=session.get('admin', False),total_received=total_received)

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
                quantity = float(val)
                if quantity > 0:
                    label = LABELS.get(key, key)
                    unit = UNITS.get(key, "each")
                    total += quantity * price
                    qty_str = int(quantity) if quantity.is_integer() else quantity
                    items_ordered.append(f"{label}: {qty_str} {unit}")
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
        new_order = Order(
            user_id=user.id,
            items_ordered=items_str,
            total_price_usd=total
        )
        db.session.add(new_order)

    db.session.commit()
    return redirect('/dashboard')


### Adninistrative Features ###
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

    order = db.get_or_404(Order, order_id)

    # ✅ Skip goat share validation
    order.status = 'Confirmed'
    db.session.commit()
    return redirect(request.args.get('next', '/dashboard'))  # ✅ Support dynamic redirect

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
    Order.query.filter_by(source="regular").delete()
    db.session.commit()
    return redirect('/dashboard')

# Admin User editing the orders
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403

    order = db.get_or_404(Order, order_id)

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
                part = order.items_ordered.split(label + ":")[1].split(",")[0].strip().split()[0]
                quantities[key] = int(float(part))
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

# Admin User exporting the confirmed orders as pdf 
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

    confirmed_orders = Order.query.filter_by(status='Confirmed', source='regular').all()

    # Table header
    data = [["Name", "Phone", "Items Ordered", "Total Paid (excl. Shp Cost)"]]

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

# Admin User deleting order 
@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    order = db.get_or_404(Order, order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(request.args.get('next', '/dashboard'))

# Admin update payments
@app.route('/update_payment/<int:order_id>', methods=['POST'])
def update_payment(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    order = db.get_or_404(Order, order_id)
    new_amount = request.form.get('amount_paid')
    try:
        order.amount_paid = float(new_amount)
        db.session.commit()
    except:
        pass  # Handle bad inputs gracefully
    return redirect('/dashboard')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)



