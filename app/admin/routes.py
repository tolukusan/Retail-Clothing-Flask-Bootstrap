# app\admin\routes.py
# Admin routes for managing dashboard, users, products, and orders.

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
# Blueprint: grouping for routes (admin_bp defined elsewhere).
# render_template: render HTML templates.
# request: access form and request data.
# redirect, url_for: redirect responses and build route URLs.
# flash: store short messages (success/error) to show in templates.
# current_app: reference to the Flask app instance (used for config/paths).

from flask_login import login_required, current_user
# login_required: decorator that ensures user is authenticated to access the route.
# current_user: proxy to the currently logged-in user object.

from app.models import User, Product, Order, OrderItem, CartItem  # Add CartItem here
# Import database models used in admin routes:
# User: user records.
# Product: product records.
# Order: orders.
# OrderItem: items inside orders.
# CartItem: items in user's shopping cart (used when deleting users).

from app.models import User, Product, Order, OrderItem
# Duplicate import — redundant and can be removed safely (no change at runtime).

from app.admin.forms import ProductForm, BatchUploadForm
# Import form classes for single-product add/edit and CSV batch uploads.

from app import db
# Import SQLAlchemy database instance to query/commit/rollback.

import os
# Standard library module for filesystem path operations and directory creation.

from werkzeug.utils import secure_filename
# Utility to sanitize uploaded filenames (avoid path traversal / unsafe characters).

from sqlalchemy import func
# Import SQL functions/aggregators like func.sum used in queries.

from . import admin_bp
# Import the Blueprint instance (admin_bp) defined in this package's __init__.py.

import csv
# Standard library CSV module to parse uploaded CSV files.

from io import StringIO
# String buffer wrapper used to read the uploaded CSV bytes as a text stream.

from decimal import Decimal
# Decimal type for precise monetary arithmetic and validation.

# ----------------------------- FILE UPLOAD HANDLER -----------------------------
def save_product_image(file):
    # Accepts a FileStorage object and saves it to static/uploads/products.
    # Returns a relative path to store in DB (e.g., 'uploads/products/20250101_...jpg') or None.

    if file and file.filename:
        # Ensure there's a file and the filename is not empty.

        filename = secure_filename(file.filename)
        # Sanitize the filename to remove dangerous characters.

        from datetime import datetime
        # Import datetime locally to timestamp the filename (keeps top-level imports tidy).

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        # Create a timestamp string: YYYYMMDD_HHMMSS_ used to make filenames unique.

        unique_filename = timestamp + filename
        # Prepend timestamp to sanitized filename to avoid collisions.

        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
        # Build the absolute path to the uploads folder inside the app's static folder.

        os.makedirs(upload_folder, exist_ok=True)
        # Create the folder (and parents) if it doesn't exist; exist_ok avoids exception if it does.

        file_path = os.path.join(upload_folder, unique_filename)
        # Full filesystem path where the file will be saved.

        file.save(file_path)
        # Save the uploaded file to disk.

        return f"uploads/products/{unique_filename}"
        # Return the relative path used by templates/DB (no leading 'static/').

    return None
    # If no file provided, return None (caller can handle absence of image).

# ----------------------------- ADMIN DASHBOARD -----------------------------
@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    # Route: /admin — main admin dashboard. Requires login.

    if not current_user.is_admin:
        # Check admin privilege on the current_user object.

        flash('Access denied. Admin privileges required.', 'error')
        # Flash an error message for non-admin attempts.

        return redirect(url_for('main.index'))
        # Redirect non-admins back to the main index page.

    total_users = User.query.count()
    # Count total users in the database.

    total_products = Product.query.count()
    # Count total products in the database.

    total_orders = Order.query.count()
    # Count total orders in the database.

    revenue = db.session.query(func.sum(Order.grand_total)).filter(
        Order.status == 'completed'
    ).scalar() or 0
    # Sum grand_total for orders with status 'completed'. scalar() returns None if no rows,
    # so 'or 0' ensures revenue is numeric zero instead of None.

    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    # Retrieve the 5 most recent orders sorted by order_date descending.

    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         revenue=revenue,
                         recent_orders=recent_orders)
    # Render admin dashboard template with the computed statistics.

# ----------------------------- MANAGE USERS -----------------------------
@admin_bp.route('/admin/users')
@login_required
def manage_users():
    # Route: /admin/users — list and stats for all users. Requires admin.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    users = User.query.all()
    # Retrieve all user objects.

    total_users = User.query.count()
    # Total users count.

    admin_users = User.query.filter_by(is_admin=True).count()
    # Count how many users have is_admin True.

    active_users = User.query.filter_by(is_active=True).count()
    # Count active users (is_active True).

    from datetime import datetime, timedelta
    # Local import for datetime utilities (used to compute month start).

    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Compute the first instant of the current month.

    new_this_month = User.query.filter(User.date_joined >= first_day_of_month).count()
    # Count users whose date_joined is on/after the first day of this month.

    return render_template('admin/users.html', 
                         users=users,
                         total_users=total_users,
                         admin_users=admin_users,
                         active_users=active_users,
                         new_this_month=new_this_month)
    # Render the users management template with data and stats.

# ----------------------------- MANAGE PRODUCTS -----------------------------
@admin_bp.route('/admin/products', methods=['GET', 'POST'])
@login_required
def manage_products():
    # Route: /admin/products — add single product, batch import, and list products.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    form = ProductForm()
    # Instantiate form for single product add/edit (Flask-WTF will bind request.form).

    batch_form = BatchUploadForm()
    # Instantiate form for CSV batch upload.

    # --- Single Product Add ---
    if form.validate_on_submit() and request.form.get('submit') == 'single':
        # Check that single-product form passed validation and the submit type is 'single'.

        image_path = None
        # Initialize image_path; will remain None if no image uploaded.

        if form.image.data:
            image_path = save_product_image(form.image.data)
            # If an image file is present, save it and get the relative path.

        product = Product(
            name=form.name.data,
            category=form.category.data,
            price=form.price.data,
            stock_level=form.stock_level.data,
            desc=form.description.data,
            image_url=image_path,
            sku=f"{form.category.data}_{Product.query.count() + 1}"
        )
        # Construct a Product model instance with data from the form.
        # SKU is generated using category and current product count + 1 (simple approach).

        db.session.add(product)
        # Stage the new product for insertion.

        db.session.commit()
        # Commit the transaction (persist product to DB).

        flash('Product added successfully!', 'success')
        # Notify admin that product was added.

        return redirect(url_for('admin.manage_products'))
        # Redirect to the same page (PRG pattern to avoid form re-submit).

    # --- Batch CSV Upload ---
    if batch_form.validate_on_submit() and request.form.get('submit') == 'batch':
        # Check that batch upload form passed validation and submit type is 'batch'.

        file = batch_form.csv_file.data
        # Get the uploaded FileStorage object from the form.

        stream = StringIO(file.stream.read().decode("UTF-8"), newline=None)
        # Read bytes from file.stream, decode to text, and wrap in StringIO for CSV reader.

        csv_reader = csv.DictReader(stream)
        # DictReader maps each CSV row to a dict using header row as keys.

        imported = 0
        # Counter for successfully imported rows.

        errors = []
        # List to accumulate row-level error messages.

        for row_num, row in enumerate(csv_reader, start=2):  # start=2 → skip header
            # Iterate CSV rows with a row number (start=2 since row 1 is header).

            try:
                name = row.get('name', '').strip()
                # Get 'name' column; default to empty string and strip whitespace.

                category = row.get('category', '').strip().lower()
                # Get category, strip whitespace, normalize to lowercase.

                price_str = row.get('price', '').strip()
                stock_str = row.get('stock_level', '').strip()
                desc = row.get('description', '').strip()
                # Extract other fields (price, stock_level, description).

                if not all([name, category, price_str, stock_str]):
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue
                # If any required field missing or empty, record error and skip row.

                if category not in ['handbag', 'watch']:
                    errors.append(f"Row {row_num}: Invalid category '{category}'")
                    continue
                # Validate category against allowed list.

                try:
                    price = Decimal(price_str)
                    if price < 0.01:
                        raise ValueError
                except:
                    errors.append(f"Row {row_num}: Invalid price '{price_str}'")
                    continue
                # Parse price as Decimal and ensure minimum price threshold.

                try:
                    stock_level = int(stock_str)
                    if stock_level < 0:
                        raise ValueError
                except:
                    errors.append(f"Row {row_num}: Invalid stock '{stock_str}'")
                    continue
                # Parse stock level and ensure non-negative integer.

                image_url = row.get('image_url', '').strip()
                # Optional image_path column from CSV.

                if image_url:
                    image_url = image_url.lstrip('/')
                    # Remove leading slash if user included one.

                    if image_url.startswith('static/'):
                        image_url = image_url[7:]
                    # Strip leading 'static/' if present to normalize path.

                    if not image_url.startswith('uploads/products/'):
                        errors.append(f"Row {row_num}: image_url must be in uploads/products/")
                        image_url = None
                    # Enforce that CSV image_url points to uploads/products/ to avoid arbitrary paths.

                else:
                    image_url = None
                # If no image_url provided, keep it None.

                sku = f"{category}_{Product.query.count() + imported + 1}"
                # Generate SKU using current product count plus imported offset to avoid collisions.

                product = Product(
                    name=name,
                    category=category,
                    price=price,
                    stock_level=stock_level,
                    desc=desc or None,
                    image_url=image_url or None,
                    sku=sku
                )
                # Create Product instance from validated CSV row.

                db.session.add(product)
                # Stage product for insertion.

                imported += 1
                # Increment imported counter for successful staging.

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                # Catch-all: record unexpected exceptions per row and continue.

        # After processing all rows, commit if at least one product staged.
        if imported > 0:
            try:
                db.session.commit()
                flash(f'Successfully imported {imported} products!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving to database: {e}', 'danger')
            # Commit transaction; rollback and flash error if commit fails.
        else:
            flash('No products imported.', 'warning')
            # Inform admin if nothing was imported.

        if errors:
            flash(f'Errors: {" | ".join(errors[:5])}' + (f" (+{len(errors)-5} more)" if len(errors)>5 else ""), 'danger')
        # If errors exist, flash up to first 5 and show count of remaining.

        return redirect(url_for('admin.manage_products'))
        # Redirect to avoid re-submission and show flash messages.

    products = Product.query.all()
    # Retrieve all products for display on the page.

    products = Product.query.all()
    # Duplicate line (redundant) — harmless but can be removed.

    return render_template(
        'admin/products.html',
        products=products,
        form=form,
        batch_form=batch_form
    )
    # Render products management template with list and both forms.

# ----------------------------- MANAGE ORDERS -----------------------------
@admin_bp.route('/admin/orders')
@login_required
def manage_orders():
    # Route: /admin/orders — list orders and provide order statistics.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    orders = Order.query.order_by(Order.order_date.desc()).all()
    # Fetch all orders ordered by most recent first.

    total_revenue = db.session.query(func.sum(Order.grand_total)).filter(
        Order.status == 'completed'
    ).scalar() or 0
    # Compute total revenue from completed orders (safe default 0).

    pending_orders = Order.query.filter_by(status='pending').count()
    # Count orders with status 'pending'.

    completed_orders = Order.query.filter_by(status='completed').count()
    # Count orders with status 'completed'.

    processing_orders = Order.query.filter_by(status='Processing').count()
    # Count orders with status 'Processing' (note capitalization may be inconsistent).

    return render_template('admin/orders.html', 
                         orders=orders,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders,
                         completed_orders=completed_orders,
                         processing_orders=processing_orders)
    # Render orders template with orders list and stats.

# ----------------------------- EDIT PRODUCT -----------------------------
@admin_bp.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    # Route: edit product page for a specific product id.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    product = Product.query.get_or_404(product_id)
    # Load product or raise 404 if not found.

    form = ProductForm(obj=product)
    # Pre-populate form with product data using WTForms' obj parameter.

    if form.validate_on_submit():
        # If form posted and valid, update product.

        if form.image.data:
            image_path = save_product_image(form.image.data)
            product.image_url = image_path
        # If a new image was uploaded, save it and update image_url.

        product.name = form.name.data
        product.category = form.category.data
        product.price = form.price.data
        product.stock_level = form.stock_level.data
        product.desc = form.description.data
        # Update product attributes from form fields.

        db.session.commit()
        # Persist changes to DB.

        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
        # Redirect after successful update.

    return render_template('admin/edit_product.html', form=form, product=product)
    # Render the edit product form (GET) or re-render on validation failure.

# ----------------------------- DELETE PRODUCT -----------------------------
@admin_bp.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    # Route: handle POST delete request for a product.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    product = Product.query.get_or_404(product_id)
    # Load product or 404 if not found.

    db.session.delete(product)
    # Mark product for deletion.

    db.session.commit()
    # Commit deletion.

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.manage_products'))
    # Redirect back to products list.

# ----------------------------- UPDATE ORDER STATUS -----------------------------
@admin_bp.route('/admin/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    # Route: update an order's status (expects form data with 'status').

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    order = Order.query.get_or_404(order_id)
    # Load order or 404.

    new_status = request.form.get('status')
    # Get the new status value from the submitted form.

    if new_status in ['pending', 'processing', 'shipped', 'completed', 'cancelled', 'Processing']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.order_id} status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'error')
    # Validate allowed statuses, commit and flash success; otherwise flash error.

    return redirect(url_for('admin.manage_orders'))
    # Redirect back to orders list.

# ----------------------------- ADD PRODUCT (EMPTY FORM) -----------------------------
@admin_bp.route('/admin/add_product')
@login_required
def add_product():
    # Route: show empty product form for adding a new product.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    form = ProductForm()
    # New empty ProductForm instance.

    return render_template('admin/edit_product.html', form=form, product=None)
    # Reuse edit_product template to display blank form (product None indicates create mode).

# ----------------------------- ORDER DETAILS PAGE -----------------------------
@admin_bp.route('/admin/orders/<int:order_id>')
@login_required
def order_details(order_id):
    # Route: show detailed view for a specific order.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    order = Order.query.get_or_404(order_id)
    # Load order and return 404 if not found.

    return render_template('admin/order_details.html', order=order)
    # Render order details template with the order object.

# ----------------------------- DELETE USER -----------------------------
@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    # Route: delete a user and related data (cart items and orders).
    # Uses POST to avoid accidental deletion via GET.

    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

    # Prevent self-deletion for safety.
    if user_id == current_user.user_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(user_id)
    # Load the user or return 404.

    try:
        CartItem.query.filter_by(user_id=user_id).delete()
        # Delete all cart items belonging to the user in a single query.

        user_orders = Order.query.filter_by(user_id=user_id).all()
        # Fetch all orders for the user to delete their items first.

        for order in user_orders:
            OrderItem.query.filter_by(order_id=order.order_id).delete()
            db.session.delete(order)
        # For each order: delete its OrderItem rows, then delete the Order record itself.

        db.session.delete(user)
        # Delete the user record.

        db.session.commit()
        # Commit transaction (deleting cart items, order items, orders, and user).

        flash(f'User {user.name} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        # Rollback any partial changes if an error occurred.

        flash('Error deleting user. Please try again.', 'error')
        print(f"Error deleting user: {e}")
        # Print/log the exception for debugging (server-side).

    return redirect(url_for('admin.manage_users'))
    # Redirect back to manage users page after attempt.
