# app/main/routes.py
from flask import render_template
from . import main_bp
from app.models import Product # Import your new models!

@main_bp.route('/')
def index():
    # Fetch products for the homepage/listing
    products = Product.query.limit(8).all()
    return render_template('main/index.html', products=products)

@main_bp.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('main/product_list.html', products=products)

@main_bp.route('/product/<int:prod_id>')
def product_detail(prod_id):
    """Displays detailed information for a single product."""
    # Fetches the product or returns a 404 Not Found error
    product = Product.query.get_or_404(prod_id)
    return render_template('main/product_detail.html', product=product)

