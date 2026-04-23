"""
config.py
---------
Classes de configuration pour les différents environnements.
Chargées via la factory create_app() dans app/__init__.py
"""

import os
from dotenv import load_dotenv

# Charge les variables depuis le fichier .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuration de base — partagée par tous les environnements."""

    # Sécurité
    SECRET_KEY = os.environ.get("SECRET_KEY") or "fallback-secret-key-change-me"
    WTF_CSRF_ENABLED = True

    # Base de données
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload fichiers
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Mo max
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}

    # Pagination
    PROJECTS_PER_PAGE = 10

    # Email
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")


class DevelopmentConfig(Config):
    """Environnement de développement local."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "projet_univ.db")
    SQLALCHEMY_ECHO = True  # Affiche les requêtes SQL dans le terminal


class TestingConfig(Config):
    """Environnement de test — base de données en mémoire."""

    TESTING = True
    WTF_CSRF_ENABLED = False  # Désactivé pour simplifier les tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Environnement de production."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "projet_univ_prod.db")


# Dictionnaire de sélection de config selon l'environnement
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}