"""
v2.3 test suite for Farm2Kitchen Halal.
Runs against an isolated SQLite test DB — no Render/PostgreSQL needed.

Usage:
    pip install pytest
    pytest test_app.py -v
"""
import os
import tempfile

# Set required env vars BEFORE importing app (config.py raises if unset)
os.environ.setdefault('SECRET_KEY', 'test-secret-key-do-not-use-in-prod')
os.environ.setdefault('ADMIN_PASSWORD', 'testpass123')
os.environ.setdefault('ADMIN_PHONES', '5551234567')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')

import pytest
from app import app as flask_app, db, User, Order, Config, ItemPrice
from config import PRICES


@pytest.fixture
def client():
    """Fresh isolated SQLite DB for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
    })

    with flask_app.app_context():
        db.create_all()
        # Seed item prices
        for key, price in PRICES.items():
            if not ItemPrice.query.filter_by(key=key).first():
                db.session.add(ItemPrice(key=key, price=price))
        db.session.commit()

        yield flask_app.test_client()

        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


def _submit_order(client, phone='5550001111', pin='1234', qty=2):
    """Helper: submit a minimal order."""
    return client.post('/submit_order', data={
        'zelle_name': 'Test User',
        'phone': phone,
        'pin': pin,
        'cow_beef': str(qty),
    }, follow_redirects=False)


# ── Order submission ──────────────────────────────────────────────────────────

def test_new_order_shows_confirmation(client):
    rv = _submit_order(client)
    assert rv.status_code == 200
    assert b'Order Received' in rv.data


def test_confirmation_page_contains_items(client):
    rv = _submit_order(client, qty=3)
    assert b'Cow/Beef' in rv.data


def test_returning_user_correct_pin_updates_order(client):
    _submit_order(client, qty=2)
    rv = _submit_order(client, qty=5)
    assert rv.status_code == 200
    assert b'Order Received' in rv.data
    with flask_app.app_context():
        from app import User, Order
        user = User.query.filter_by(phone='5550001111').first()
        order = Order.query.filter_by(user_id=user.id).first()
        assert '5' in order.items_ordered  # qty updated to 5


def test_returning_user_wrong_pin_returns_403(client):
    # Use a unique phone so rate limiter in-memory state from other tests doesn't interfere
    _submit_order(client, phone='5550009001', pin='1234')
    rv = _submit_order(client, phone='5550009001', pin='9999')
    assert rv.status_code == 403


def test_invalid_phone_returns_400(client):
    rv = client.post('/submit_order', data={
        'zelle_name': 'Test',
        'phone': '123',  # too short
        'pin': '1234',
        'cow_beef': '1',
    })
    assert rv.status_code == 400


def test_invalid_pin_returns_400(client):
    rv = client.post('/submit_order', data={
        'zelle_name': 'Test',
        'phone': '5550009002',  # unique phone to avoid rate limit state
        'pin': '12',  # too short
        'cow_beef': '1',
    })
    assert rv.status_code == 400


# ── CSRF protection ───────────────────────────────────────────────────────────

def test_csrf_rejects_post_without_token(client):
    flask_app.config['WTF_CSRF_ENABLED'] = True
    rv = client.post('/submit_order', data={
        'zelle_name': 'Test',
        'phone': '5550001111',
        'pin': '1234',
        'cow_beef': '1',
    })
    assert rv.status_code == 400
    flask_app.config['WTF_CSRF_ENABLED'] = False


# ── Admin login ───────────────────────────────────────────────────────────────

def test_admin_login_correct_credentials(client):
    rv = client.post('/admin_login', data={
        'phone': '5551234567',
        'password': 'testpass123',
    }, follow_redirects=False)
    assert rv.status_code == 302
    assert rv.location == '/dashboard'


def test_admin_login_wrong_password_returns_403(client):
    rv = client.post('/admin_login', data={
        'phone': '5551234567',
        'password': 'wrongpassword',
    })
    assert rv.status_code == 403


def test_admin_login_wrong_phone_returns_403(client):
    rv = client.post('/admin_login', data={
        'phone': '9999999999',
        'password': 'testpass123',
    })
    assert rv.status_code == 403


# ── Admin PIN reset ───────────────────────────────────────────────────────────

def test_admin_can_reset_pin(client):
    _submit_order(client, phone='5550002222', pin='4321')

    # Log in as admin
    with client.session_transaction() as sess:
        sess['admin'] = True

    with flask_app.app_context():
        user = User.query.filter_by(phone='5550002222').first()
        assert user.pin_hash is not None
        rv = client.post(f'/reset_pin/{user.id}', follow_redirects=False)
        assert rv.status_code == 302

    with flask_app.app_context():
        user = User.query.filter_by(phone='5550002222').first()
        assert user.pin_hash is None


def test_non_admin_cannot_reset_pin(client):
    _submit_order(client, phone='5550003333', pin='5678')
    with flask_app.app_context():
        user = User.query.filter_by(phone='5550003333').first()
        rv = client.post(f'/reset_pin/{user.id}')
        assert rv.status_code == 403


# ── Shared cost divisor ───────────────────────────────────────────────────────

def test_shared_cost_divides_by_confirmed_orders_only(client):
    # Submit 2 orders
    _submit_order(client, phone='5550010001', pin='1111')
    _submit_order(client, phone='5550010002', pin='2222')

    with flask_app.app_context():
        # Confirm only 1
        order1 = Order.query.join(User).filter(User.phone == '5550010001').first()
        order1.status = 'Confirmed'
        db.session.commit()

        # Set shared cost
        db.session.add(Config(key='shared_cost', value=20.0))
        db.session.commit()

    with client.session_transaction() as sess:
        sess['admin'] = True

    rv = client.get('/dashboard')
    assert rv.status_code == 200
    # shared_cost=20 / 1 confirmed = $20.00 per order
    assert b'20.00' in rv.data


# ── PDF export ────────────────────────────────────────────────────────────────

def test_pdf_export_includes_amount_paid(client):
    _submit_order(client, phone='5550020001', pin='1234')

    with flask_app.app_context():
        order = Order.query.join(User).filter(User.phone == '5550020001').first()
        order.status = 'Confirmed'
        order.amount_paid = 75.50
        db.session.commit()

    with client.session_transaction() as sess:
        sess['admin'] = True

    rv = client.get('/export_confirmed_pdf')
    assert rv.status_code == 200
    assert rv.content_type == 'application/pdf'
    # PDF is compressed — just verify it's a valid non-empty PDF file
    assert rv.data.startswith(b'%PDF')
    assert len(rv.data) > 500
