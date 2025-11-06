# run.py
from app import create_app
# Ensure you import the global placeholder for Celery from app/__init__.py

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
