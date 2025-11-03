from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import User, Product, Order, OrderItem, CartItem  # Add CartItem here
from app.models import User, Product, Order, OrderItem
from app.admin.forms import ProductForm
from app import db
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# Add this function to handle file uploads
def save_product_image(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Create unique filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        unique_filename = timestamp + filename
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
        
        # Create folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return f"/static/uploads/products/{unique_filename}"
    return None

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get real data from database
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    
    # Calculate actual revenue from completed orders using grand_total
    revenue = db.session.query(func.sum(Order.grand_total)).filter(
        Order.status == 'completed'
    ).scalar() or 0
    
    # Get recent orders for the dashboard (last 5 orders)
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         revenue=revenue,
                         recent_orders=recent_orders)

@admin_bp.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Calculate users joined this month
    from datetime import datetime, timedelta
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = User.query.filter(User.date_joined >= first_day_of_month).count()
    
    return render_template('admin/users.html', 
                         users=users,
                         total_users=total_users,
                         admin_users=admin_users,
                         active_users=active_users,
                         new_this_month=new_this_month)

@admin_bp.route('/admin/products', methods=['GET', 'POST'])
@login_required
def manage_products():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    form = ProductForm()
    
    if form.validate_on_submit():
        # Handle image upload
        image_path = None
        if form.image.data:
            image_path = save_product_image(form.image.data)
        
        # Create new product
        product = Product(
            name=form.name.data,
            category=form.category.data,
            price=form.price.data,
            stock_level=form.stock_level.data,
            desc=form.description.data,
            image_url=image_path,
            sku=f"{form.category.data}_{Product.query.count() + 1}"
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
    
    products = Product.query.all()
    return render_template('admin/products.html', products=products, form=form)

@admin_bp.route('/admin/orders')
@login_required
def manage_orders():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    orders = Order.query.order_by(Order.order_date.desc()).all()
    
    # Calculate additional order statistics
    total_revenue = db.session.query(func.sum(Order.grand_total)).filter(
        Order.status == 'completed'
    ).scalar() or 0
    
    pending_orders = Order.query.filter_by(status='pending').count()
    completed_orders = Order.query.filter_by(status='completed').count()
    processing_orders = Order.query.filter_by(status='Processing').count()
    
    return render_template('admin/orders.html', 
                         orders=orders,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders,
                         completed_orders=completed_orders,
                         processing_orders=processing_orders)

@admin_bp.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_path = save_product_image(form.image.data)
            product.image_url = image_path
        
        product.name = form.name.data
        product.category = form.category.data
        product.price = form.price.data
        product.stock_level = form.stock_level.data
        product.desc = form.description.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
    
    return render_template('admin/edit_product.html', form=form, product=product)

@admin_bp.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/admin/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'shipped', 'completed', 'cancelled', 'Processing']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.order_id} status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'error')
    
    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/admin/add_product')
@login_required
def add_product():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    form = ProductForm()
    return render_template('admin/edit_product.html', form=form, product=None)

@admin_bp.route('/admin/orders/<int:order_id>')
@login_required
def order_details(order_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_details.html', order=order)

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Prevent users from deleting themselves
    if user_id == current_user.user_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        # Delete user's cart items first
        CartItem.query.filter_by(user_id=user_id).delete()
        
        # Delete user's orders and order items
        user_orders = Order.query.filter_by(user_id=user_id).all()
        for order in user_orders:
            OrderItem.query.filter_by(order_id=order.order_id).delete()
            db.session.delete(order)
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {user.name} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Please try again.', 'error')
        print(f"Error deleting user: {e}")
    
    return redirect(url_for('admin.manage_users'))