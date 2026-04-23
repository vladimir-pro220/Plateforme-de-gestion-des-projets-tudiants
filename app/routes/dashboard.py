"""
routes/dashboard.py
-------------------
Blueprint dashboard : redirige vers le tableau de bord selon le rôle.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.application import Application
from app.utils.helpers import get_global_stats, get_teacher_stats, get_student_stats

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """Page d'accueil publique."""
    from app.utils.helpers import get_global_stats

    stats = get_global_stats()
    projects = (
        Project.query.filter_by(status="open").order_by(Project.created_at.desc()).limit(6).all()
    )
    return render_template("index.html", stats=stats, projects=projects, title="Accueil")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Redirige vers le dashboard selon le rôle de l'utilisateur."""
    if current_user.is_student:
        return redirect(url_for("dashboard.student_dashboard"))
    elif current_user.is_teacher:
        return redirect(url_for("dashboard.teacher_dashboard"))
    elif current_user.is_admin:
        return redirect(url_for("dashboard.admin_dashboard"))
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/dashboard/student")
@login_required
def student_dashboard():
    """Tableau de bord étudiant."""
    if not current_user.is_student:
        return redirect(url_for("dashboard.dashboard"))

    stats = get_student_stats(current_user.id)
    recent_applications = (
        Application.query.filter_by(student_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )
    open_projects = (
        Project.query.filter_by(status="open").order_by(Project.created_at.desc()).limit(5).all()
    )

    return render_template(
        "dashboard/student.html",
        stats=stats,
        recent_applications=recent_applications,
        open_projects=open_projects,
        title="Mon tableau de bord",
    )


@dashboard_bp.route("/dashboard/teacher")
@login_required
def teacher_dashboard():
    """Tableau de bord enseignant."""
    if not current_user.is_teacher:
        return redirect(url_for("dashboard.dashboard"))

    stats = get_teacher_stats(current_user.id)
    my_projects = (
        Project.query.filter_by(teacher_id=current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )

    # Candidatures en attente sur tous mes projets
    project_ids = [p.id for p in my_projects]
    pending_applications = (
        Application.query.filter(
            Application.project_id.in_(project_ids),
            Application.status == "pending",
        )
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/teacher.html",
        stats=stats,
        my_projects=my_projects,
        pending_applications=pending_applications,
        title="Mon tableau de bord",
    )


@dashboard_bp.route("/dashboard/admin")
@login_required
def admin_dashboard():
    """Tableau de bord administrateur."""
    if not current_user.is_admin:
        return redirect(url_for("dashboard.dashboard"))

    stats = get_global_stats()
    return render_template("dashboard/admin.html", stats=stats, title="Administration")
