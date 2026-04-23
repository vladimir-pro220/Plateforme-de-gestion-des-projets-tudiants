"""
app/routes/__init__.py
----------------------
Enregistrement de tous les blueprints dans la factory create_app().
Chaque blueprint est importé et retourné via register_blueprints()
pour être appelé depuis app/__init__.py.
"""

from app.routes.auth import auth_bp
from app.routes.projects import projects_bp
from app.routes.applications import applications_bp
from app.routes.dashboard import dashboard_bp
from app.routes.admin import admin_bp
from app.routes.export import export_bp


def register_blueprints(app):
    """Enregistre tous les blueprints Flask dans l'application.

    Args:
        app: L'instance Flask créée par create_app().
    """
    app.register_blueprint(auth_bp)  # /auth/login  /auth/register  /auth/logout
    app.register_blueprint(projects_bp)  # /projects/
    app.register_blueprint(applications_bp)  # /applications/
    app.register_blueprint(dashboard_bp)  # /dashboard/
    app.register_blueprint(admin_bp)  # /admin/
    app.register_blueprint(export_bp)  # /export/
