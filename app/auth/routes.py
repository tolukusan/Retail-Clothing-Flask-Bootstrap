# File: app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth.forms import RegistrationForm, LoginForm
from . import auth_bp
from app.models import User, db
from flask_login import (
    login_user,
    current_user,
    logout_user,
)  
from app.tasks import send_welcome_email


# --- A. Registration Route ---
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Using British English for the flash message
            flash("That email address is already registered. Please log in.", "warning")
            return redirect(url_for("auth.register"))

        # Create new user
        hashed_password = generate_password_hash(
            form.password.data, method="pbkdf2:sha256"
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=hashed_password,
            wallet_balance=0.00,  # Initialise the wallet balance
        )

        # Save to database
        send_welcome_email(form.email.data, form.name.data) 
        db.session.add(new_user)
        db.session.commit()
        

        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


# --- B. Login Route ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Welcome back!", "info")
            return redirect(url_for("main.index")) 
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")

    return render_template("auth/login.html", form=form)


# --- C. Logout Route ---
@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Logs out the current user and redirects to the homepage."""
    # This function removes the user ID from the session, effectively logging the user out.
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("main.index"))