from app import create_app, db  
# Imports the 'create_app' function and the database object 'db' from the 'app' package.
# 'create_app' is usually a factory function that creates and configures a Flask application instance.
# 'db' is the SQLAlchemy database instance used for interacting with the database.

from app.models import User  
# Imports the 'User' model from the 'models' module inside the 'app' package.
# This lets us query the User table in the database.

app = create_app()  
# Calls the 'create_app()' function to create an instance of the Flask application.
# This initializes the app with all configurations, blueprints, and extensions.

with app.app_context():  
    # Creates an application context.
    # Flask needs an app context to access resources like the database, configuration, and models.
    # Without this, database queries would raise a “Working outside of application context” error.

    users = User.query.all()  
    # Queries the database for all rows in the User table.
    # Returns a list of User objects.

    print("=== ALL USERS ===")  
    # Prints a header for clarity in the output.

    for user in users:  
        # Loops through each user object retrieved from the database.

        print(f"ID: {user.user_id} | Name: {user.name} | Email: {user.email} | Admin: {user.is_admin}")  
        # Prints out each user's details in a formatted string.
        # Shows the user's ID, name, email, and whether they are an admin.

    print("=================")  
    # Prints a footer line to mark the end of the output.
