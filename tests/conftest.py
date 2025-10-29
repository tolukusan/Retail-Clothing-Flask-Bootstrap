import pytest
from app import (
    create_app,
    db,
)  # Assuming you have an Application Factory called create_app


@pytest.fixture()
def app():
    # 1. Create a testing instance of your app
    app = create_app(
        {
            "TESTING": True,
            # Set a temporary database URI for testing (e.g., in-memory SQLite)
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    # 2. Set up the application context
    with app.app_context():
        # You'll usually initialise and populate your test database here
        db.create_all()
        pass

    yield app

    # 3. Clean up the application context if needed
    db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
