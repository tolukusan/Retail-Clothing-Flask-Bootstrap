from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.get(2)  # ID 2 - Onyinyechi
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"SUCCESS! User {user.name} is now admin!")
    else:
        print("User not found")