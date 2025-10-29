# __init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder="templates")
    app.config.from_object(Config)
    app.config.from_pyfile("config.py", silent=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Flask-Login settings
    login_manager.login_view = "auth.login"  # redirect unauth users here
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    from . import models
    
    # User loader (required by Flask-Login)
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User

        return User.query.get(int(user_id))

    
    # Import and register routes
    from app.main import main_bp
    from app.auth import auth_bp
    from app.cart import cart_bp
    from app.wallet import wallet_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wallet_bp)

    return app
