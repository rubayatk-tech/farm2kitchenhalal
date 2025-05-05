from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
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
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.Float)

@app.route('/')
def index():
    return render_template('index.html', prices=PRICES, labels=LABELS)

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

@app.route('/submit_order', methods=['POST'])
def submit_order():
    zelle_name = request.form.get('zelle_name')
    phone = request.form.get('phone')

    # 🔐 Validate phone number is exactly 10 digits
    if not phone.isdigit() or len(phone) != 10:
        return "Phone number must be exactly 10 digits.", 400
    
    items_ordered = []
    total = 0.0
    for key, price in PRICES.items():
        val = request.form.get(key)
        if val and float(val) > 0:
            total += float(val) * price
            label = LABELS.get(key, key)
            items_ordered.append(f"{label}: {val}")

    items_str = ', '.join(items_ordered) if items_ordered else "No items"
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(zelle_name=zelle_name, phone=phone)
        db.session.add(user)
        db.session.commit()

    existing_order = Order.query.filter_by(user_id=user.id).first()
    if existing_order:
        existing_order.items_ordered = items_str
        existing_order.total_price_usd = total
    else:
        new_order = Order(user_id=user.id, items_ordered=items_str, total_price_usd=total)
        db.session.add(new_order)

    db.session.commit()
    return redirect('/dashboard')

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

@app.route('/confirm_order/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    order = Order.query.get_or_404(order_id)
    order.status = 'Confirmed'
    db.session.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/dashboard')

@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if not session.get('admin'):
        return "Unauthorized", 403
    Order.query.delete()
    db.session.commit()
    return redirect('/dashboard')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


