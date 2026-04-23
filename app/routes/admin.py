"""
routes/admin.py
---------------
Blueprint admin : gestion des utilisateurs et statistiques globales.
Accès réservé aux administrateurs uniquement.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.user import User
from app.models.project import Project
from app.models.application import Application
from app.utils.decorators import admin_required
from app.utils.helpers import get_global_stats

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    """Liste de tous les utilisateurs."""
    page = request.args.get("page", 1, type=int)
    role_filter = request.args.get("role", "")
    search = request.args.get("search", "").strip()

    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%"))
            | (User.first_name.ilike(f"%{search}%"))
            | (User.last_name.ilike(f"%{search}%"))
        )

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    return render_template(
        "admin/users.html",
        users=users,
        role_filter=role_filter,
        search=search,
        title="Gestion des utilisateurs",
    )


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    """Active ou désactive un compte utilisateur."""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = "activé" if user.is_active else "désactivé"
    flash(f"Compte de {user.full_name} {status}.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    """Supprime un utilisateur."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"Utilisateur {user.full_name} supprimé.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/stats")
@login_required
@admin_required
def stats():
    """Page de statistiques globales."""
    stats = get_global_stats()

    # Projets par domaine
    from sqlalchemy import func

    projects_by_domain = (
        db.session.query(Project.domain, func.count(Project.id)).group_by(Project.domain).all()
    )

    # Projets par statut
    projects_by_status = (
        db.session.query(Project.status, func.count(Project.id)).group_by(Project.status).all()
    )

    # Candidatures par statut
    apps_by_status = (
        db.session.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )

    return render_template(
        "admin/stats.html",
        stats=stats,
        projects_by_domain=projects_by_domain,
        projects_by_status=projects_by_status,
        apps_by_status=apps_by_status,
        title="Statistiques globales",
    )
