# app/models.py
from . import db
from flask_login import UserMixin  # A helper class for user authentication
from decimal import Decimal


# --- 1. User Table ---
class User(UserMixin, db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    # Wallet balance initialised to 0.00
    wallet_balance = db.Column(db.Numeric(10, 2), default=0.00)


    is_admin = db.Column(db.Boolean, default=False)  
    is_active = db.Column(db.Boolean, default=True)  
    date_joined = db.Column(db.DateTime, default=db.func.now())  

    # Note: Flask-Login expects a method named 'get_id()', but UserMixin provides it.
    # To keep your existing column name, you need to override the default:
    def get_id(self):
        return self.user_id


# --- 2. Product Table ---
class Product(db.Model):
    __tablename__ = "product"
    prod_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    desc = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_level = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), nullable=False)  # 'watch' or 'bag'
    image_url = db.Column(db.String(255))


# --- 3. Cart Items Table ---
class CartItem(db.Model):
    __tablename__ = "cart_item"
    cart_item_id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    prod_id = db.Column(db.Integer, db.ForeignKey("product.prod_id"), nullable=False)

    qty = db.Column(db.Integer, default=1)

    # Relationships (Optional but helpful for querying)
    user = db.relationship("User", backref=db.backref("cart_items", lazy=True))
    product = db.relationship("Product")


# --- 4. Order Table ---
class Order(db.Model):
    __tablename__ = "order"
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(50), default="Processing")
    payment_method = db.Column(db.String(50), nullable=False)

    # Relationship to get all items in this order
    items = db.relationship("OrderItem", backref="order", lazy="dynamic")
    user = db.relationship("User")
    sub_total = db.Column(db.Numeric(10, 2), nullable=False)
    grand_total = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_cost = db.Column(db.Numeric(10, 2), default=Decimal('0.00'))


# --- 5. Order Items Table ---
class OrderItem(db.Model):
    __tablename__ = "order_item"
    order_item_id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey("order.order_id"), nullable=False)
    prod_id = db.Column(db.Integer, db.ForeignKey("product.prod_id"), nullable=False)

    qty = db.Column(db.Integer, default=1)
    # The crucial saved price at the time of purchase
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    product = db.relationship("Product")
    