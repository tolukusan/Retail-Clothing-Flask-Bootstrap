from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app import db 
from .forms import WalletTopUpForm 
from . import wallet_bp
from decimal import Decimal

@wallet_bp.route("/") 
@login_required
def wallet_home():
    """Renders the user's wallet homepage."""
    # The template uses current_user directly
    return render_template("wallet/index.html")

@wallet_bp.route("/topup", methods=["GET", "POST"]) 
@login_required
def top_up_wallet():
    """Handles topping up the user's wallet balance."""
    form = WalletTopUpForm()
    
    if form.validate_on_submit():
        # Ensure data is treated as Decimal for high precision
        top_up_amount = Decimal(form.amount.data)
        
        # Transaction: Add amount to wallet
        try:
            current_user.wallet_balance += top_up_amount
            db.session.commit()
            
            flash(
                f"Successfully topped up £{top_up_amount:.2f}! New balance: £{current_user.wallet_balance:.2f}", 
                "success"
            )
            # Redirect to the wallet home route within the 'wallet' blueprint
            return redirect(url_for('wallet.wallet_home')) 
            
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during the transaction. Please try again.", "danger")
            print(f"Wallet Top-Up Error: {e}")
            
    current_balance = f"£{current_user.wallet_balance:.2f}"
    
    # We use the template from the 'main' directory as it was created there
    return render_template("wallet/wallet_topup.html", form=form, current_balance=current_balance)
