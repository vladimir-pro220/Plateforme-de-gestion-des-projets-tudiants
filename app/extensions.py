"""
extensions.py
-------------
Instanciation des extensions Flask sans les lier à l'application.
Elles seront initialisées dans create_app() via la méthode init_app().
Ce pattern évite les imports circulaires.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Base de données ORM
db = SQLAlchemy()

# Gestionnaire d'authentification
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Route de redirection si non connecté
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"

# Migrations de base de données
migrate = Migrate()

# Envoi d'emails
mail = Mail()

# Protection CSRF globale
csrf = CSRFProtect()
