"""
app/__init__.py
---------------
Factory function create_app().
Initialise Flask, lie les extensions, enregistre les blueprints
et configure les handlers d'erreurs.
"""

import os
from flask import Flask
from markupsafe import Markup, escape
from config import config
from app.extensions import db, login_manager, migrate, mail, csrf


def create_app(env_name: str = "default") -> Flask:
    """
    Crée et configure l'application Flask.

    Args:
        env_name: Nom de l'environnement ('development', 'testing', 'production')

    Returns:
        Flask: Instance de l'application configurée
    """
    app = Flask(__name__)

    # ── Chargement de la configuration ──────────────────────────────────────
    app.config.from_object(config[env_name])

    # Crée le dossier instance si inexistant (pour SQLite)
    os.makedirs(app.instance_path, exist_ok=True)

    # Crée le dossier uploads si inexistant
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Initialisation des extensions ────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # ── Filtre Jinja2 personnalisé : nl2br ───────────────────────────────────
    @app.template_filter("nl2br")
    def nl2br_filter(value: str) -> Markup:
        """Convertit les sauts de ligne en balises <br> pour Jinja2."""
        if not value:
            return Markup("")
        return Markup(escape(value).replace("\n", Markup("<br>\n")))

    # ── Enregistrement des blueprints ────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.projects import projects_bp
    from app.routes.applications import applications_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.export import export_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)

    # ── Handlers d'erreurs ───────────────────────────────────────────────────
    register_error_handlers(app)

    return app


def register_error_handlers(app: Flask) -> None:
    """Enregistre les pages d'erreur personnalisées."""
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500