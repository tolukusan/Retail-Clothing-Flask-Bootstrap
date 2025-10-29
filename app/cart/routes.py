# app/cart/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from . import cart_bp
from app import db
from app.models import Product, CartItem, Order, OrderItem # Import your new models!
from decimal import Decimal

@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required # Ensure only logged-in users can add to cart
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    # Check if the item is already in the user's cart
    cart_item = CartItem.query.filter_by(
        user_id=current_user.user_id,
        prod_id=product.prod_id
    ).first()

    if cart_item:
        # Item exists, increase quantity
        cart_item.qty += 1
    else:
        # Item does not exist, create a new cart item
        cart_item = CartItem(
            user_id=current_user.user_id,
            prod_id=product.prod_id,
            qty=1
        )
        db.session.add(cart_item)

    db.session.commit()
    flash(f'Added {product.name} to your cart!', 'success')
    return redirect(url_for('main.product_list'))

# --- NEW CART ROUTES ---

@cart_bp.route('/cart')
@login_required
def view_cart():
    """Displays the user's current shopping cart and calculates the total."""
    cart_items = CartItem.query.filter_by(user_id=current_user.user_id).all()
    
    # Calculate subtotal, handling items that might have been deleted from Product table (though unlikely)
    subtotal = Decimal('0.00')
    
    # Use a dictionary to store product data alongside cart items to avoid N+1 queries later
    cart_data = []
    
    for item in cart_items:
        # The relationship (item.product) makes fetching the product efficient
        product = item.product 
        
        if product:
            item_total = product.price * item.qty
            subtotal += item_total
            cart_data.append({
                'item': item,
                'product': product,
                'item_total': item_total
            })

    # Basic shipping calculation (e.g., £5.00 flat rate for orders under £100)
    shipping = Decimal('5.00') if subtotal < Decimal('100.00') and subtotal > 0 else Decimal('0.00')
    grand_total = subtotal + shipping

    context = {
        'cart_data': cart_data,
        'subtotal': subtotal,
        'shipping': shipping,
        'grand_total': grand_total
    }
    
    return render_template('cart/cart.html', **context)


@cart_bp.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    """Removes a single item entry from the user's cart."""
    # Find the specific cart item belonging to the current user
    item_to_remove = CartItem.query.filter_by(
        user_id=current_user.user_id,
        cart_item_id=cart_item_id
    ).first_or_404()

    product_name = item_to_remove.product.name if item_to_remove.product else "Item"
    
    db.session.delete(item_to_remove)
    db.session.commit()
    
    flash(f'{product_name} was removed from your basket.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item_quantity(cart_item_id):
    """Updates the quantity of a specific item in the cart."""
    new_qty_str = request.form.get('qty', '1')
    try:
        new_qty = int(new_qty_str)
    except ValueError:
        flash('Invalid quantity provided.', 'danger')
        return redirect(url_for('cart.view_cart'))

    cart_item = CartItem.query.filter_by(
        user_id=current_user.user_id,
        cart_item_id=cart_item_id
    ).first_or_404()
    
    product = cart_item.product

    if new_qty <= 0:
        # If quantity is set to 0, remove the item entirely
        db.session.delete(cart_item)
        flash(f'Removed {product.name} from your basket.', 'info')
    elif new_qty > product.stock_level:
        # Prevent adding more than available stock
        flash(f'Sorry, only {product.stock_level} of {product.name} are currently in stock.', 'warning')
        cart_item.qty = product.stock_level
    else:
        # Update quantity
        cart_item.qty = new_qty
        flash(f'Quantity for {product.name} updated.', 'success')

    db.session.commit()
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """
    Processes the order:
    1. Validates stock and funds.
    2. Deducts amount from the user's wallet.
    3. Creates Order and OrderItem records.
    4. Reduces product stock.
    5. Clears the cart.
    """
    # 1. Fetch Cart Data
    cart_items = CartItem.query.filter_by(user_id=current_user.user_id).all()

    if not cart_items:
        flash('Your basket is empty and cannot be checked out.', 'warning')
        return redirect(url_for('cart.view_cart'))

    # Prepare for recalculation and transaction setup
    subtotal = Decimal('0.00')
    order_items_to_create = []
    
    # 2. Validation & Recalculation
    for item in cart_items:
        product = item.product
        
        # Stock Check
        if product.stock_level < item.qty:
            flash(f'Sorry, not enough stock for {product.name}. Only {product.stock_level} remaining.', 'danger')
            return redirect(url_for('cart.view_cart'))
            
        item_total = product.price * item.qty
        subtotal += item_total
        
        # Store data for atomic creation later
        order_items_to_create.append({
            'product': product,
            'qty': item.qty,
            'price_at_purchase': product.price
        })

    # Shipping/Total Calculation (consistent with view_cart)
    shipping = Decimal('5.00') if subtotal < Decimal('100.00') and subtotal > 0 else Decimal('0.00')
    grand_total = subtotal + shipping
    
    # Wallet Balance Check
    if current_user.wallet_balance < grand_total:
        flash(f'Insufficient funds. Your wallet balance is £{current_user.wallet_balance:.2f}, but the total is £{grand_total:.2f}. Please top up your wallet.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    # 3. Transaction Processing (Atomic)
    try:
        # a. Deduct from user wallet
        current_user.wallet_balance -= grand_total
        
        # b. Create new Order - UPDATED to match your Order model
        new_order = Order(
            user_id=current_user.user_id,
            sub_total=subtotal,  # Changed from total_amount
            grand_total=grand_total,  # Changed from total_amount
            shipping_cost=shipping,
            payment_method="Wallet"  # Added required field
            # order_date and status have defaults
        )
        db.session.add(new_order)
        db.session.flush() # Needed to get new_order.order_id

        # c. Create OrderItems and update stock
        for data in order_items_to_create:
            order_item = OrderItem(
                order_id=new_order.order_id,
                prod_id=data['product'].prod_id,
                qty=data['qty'],
                price_at_purchase=data['price_at_purchase']
            )
            db.session.add(order_item)
            
            # Reduce Product Stock
            data['product'].stock_level -= data['qty']
        
        # d. Delete CartItems
        CartItem.query.filter_by(user_id=current_user.user_id).delete()

        # 4. Commit Transaction
        db.session.commit()
        flash(f'Order #{new_order.order_id} successfully placed! The amount of £{grand_total:.2f} has been deducted from your wallet.', 'success')
        
        # Redirect to the homepage or an order history page
        return redirect(url_for('main.index')) 
        
    except Exception as e:
        # 5. Rollback on failure
        db.session.rollback()
        flash('A critical error occurred during checkout. Your order was not placed. Funds have not been deducted.', 'danger')
        print(f"Checkout error: {e}")
        return redirect(url_for('cart.view_cart'))

@cart_bp.route('/orders')
@login_required
def user_orders():
    """Fetches and displays the user's past order history."""
    # Fetch all orders for the current user, ordered by most recent first
    orders = Order.query.filter_by(user_id=current_user.user_id).order_by(Order.order_date.desc()).all()
    
    return render_template('cart/order_history.html', orders=orders)