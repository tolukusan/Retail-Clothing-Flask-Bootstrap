# insert_dummy_data.py
# To run: python insert_dummy_data.py

from app import create_app  # Import your application factory
from app.models import Product, db
from decimal import Decimal

# --- Data Definition ---
products_to_add = [
    Product(
        name='Classic Chronograph',
        sku='CRON-A001',
        desc='A timeless stainless steel chronograph watch with a black dial and a precise quartz movement.',
        price=Decimal('199.99'),
        stock_level=15,
        category='watch',
        image_url='https://via.placeholder.com/300/0000FF/FFFFFF?text=Blue+Watch'
    ),
    Product(
        name='Minimalist Leather Watch',
        sku='MIN-B002',
        desc='Elegant, slim-profile watch with a white face and a genuine Italian leather strap.',
        price=Decimal('125.00'),
        stock_level=22,
        category='watch',
        image_url='https://via.placeholder.com/300/808080/FFFFFF?text=Grey+Watch'
    ),
    Product(
        name='Luxury Travel Backpack',
        sku='BACK-C003',
        desc='Durable, waterproof backpack with multiple compartments, perfect for weekend trips.',
        price=Decimal('85.50'),
        stock_level=8,
        category='bag',
        image_url='https://via.placeholder.com/300/FFA500/000000?text=Orange+Backpack'
    ),
    Product(
        name='Premium Crossbody Bag',
        sku='CROSS-D004',
        desc='Compact and stylish crossbody bag made from vegan leather with gold accents.',
        price=Decimal('55.99'),
        stock_level=0, # Set to 0 to test 'Out of Stock' display
        category='bag',
        image_url='https://via.placeholder.com/300/008000/FFFFFF?text=Green+Bag'
    ),
]

# --- Core Functionality ---
def create_products():
    """Adds a selection of dummy products to the database."""
    print("--- Starting Dummy Data Insertion ---")
    
    products_added = 0
    for p in products_to_add:
        # Check if product already exists by SKU to prevent duplicates
        if not Product.query.filter_by(sku=p.sku).first():
            db.session.add(p)
            print(f"Adding product: {p.name}")
            products_added += 1
        else:
            print(f"Skipped: {p.name} (SKU already exists)")
            
    db.session.commit()
    print(f"--- Successfully added {products_added} new product(s). ---")

# --- Execution Block ---
if __name__ == '__main__':
    # 1. Create the Flask app instance
    app = create_app()
    
    # 2. Use the application context to enable database access
    with app.app_context():
        create_products()