import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration (shared across all environments)."""

    load_dotenv()

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # if os.environ.get("DATABASE_URL") is None:
    #     SQLALCHEMY_DATABASE_URI = "sqlite:///instance/app3.db"

    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
    #     basedir, "instance", "app3.db"
    # )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("DEBUG", "False").lower() in ["true", "1", "t"]


class DevelopmentConfig(Config):
    """Development-specific configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production-specific configuration."""

    DEBUG = False
