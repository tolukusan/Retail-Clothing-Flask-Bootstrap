from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("=== ALL USERS ===")
    for user in users:
        print(f"ID: {user.user_id} | Name: {user.name} | Email: {user.email} | Admin: {user.is_admin}")
    print("=================")