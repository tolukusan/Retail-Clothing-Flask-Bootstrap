# Retail Clothing Web Application (Flask & Bootstrap)

A responsive web application for a retail clothing business, built with **Flask** and styled using **Bootstrap**. Features a modular structure, SQLAlchemy ORM with Alembic migrations, dummy data seeding, and a test suite.

## Features

-   Modular Flask architecture (`/app` directory)
-   Database schema management via Flask-Migrate/Alembic (`/migrations`)
-   Dummy data insertion script (`insert_dummy_data.py`)
-   Unit and integration tests (`/tests`)
-   Dependency management via `requirements.txt`

## Installation

### Prerequisites

-   Python 3.x
-   `pip`

### Steps

1. **Clone the repository**

    ```bash
    git clone git@github.com:tolukusan/Retail-Clothing-Flask-Bootstrap.git
    cd Retail-Clothing-Flask-Bootstrap
    ```

2. **Create and activate a virtual environment**

    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Initialise database**

    ```bash
    set FLASK_APP=run.py
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. **(Optional) Insert dummy data**
    ```bash
    python insert_dummy_data.py
    ```

## Running the App

```bash
python run.py
```

Visit `http://127.0.0.1:5000` in your browser.

## Licence

MIT Licence
