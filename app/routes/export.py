"""
routes/export.py
----------------
Blueprint export : génération de fichiers CSV.
Accessible aux enseignants (leurs projets) et aux admins (tout).
"""

import csv
import io
from flask import Blueprint, Response, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.application import Application
from app.utils.decorators import role_required

export_bp = Blueprint("export", __name__, url_prefix="/export")


@export_bp.route("/projects.csv")
@login_required
@role_required("teacher", "admin")
def export_projects():
    """Exporte les projets en CSV."""
    if current_user.is_admin:
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        projects = (
            Project.query.filter_by(teacher_id=current_user.id)
            .order_by(Project.created_at.desc())
            .all()
        )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    # En-têtes
    writer.writerow(
        [
            "ID",
            "Titre",
            "Domaine",
            "Statut",
            "Max étudiants",
            "Candidatures",
            "Enseignant",
            "Date création",
        ]
    )

    # Données
    for p in projects:
        writer.writerow(
            [
                p.id,
                p.title,
                p.domain,
                p.status_label,
                p.max_students,
                p.applications_count,
                p.teacher.full_name,
                p.created_at.strftime("%d/%m/%Y"),
            ]
        )

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=projets.csv"},
    )


@export_bp.route("/applications/<int:project_id>.csv")
@login_required
@role_required("teacher", "admin")
def export_applications(project_id):
    """Exporte les candidatures d'un projet en CSV."""
    project = Project.query.get_or_404(project_id)

    if not current_user.is_admin and project.teacher_id != current_user.id:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("dashboard.index"))

    applications = (
        Application.query.filter_by(project_id=project_id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow(["ID", "Étudiant", "Email", "Statut", "CV", "Date candidature"])

    for a in applications:
        writer.writerow(
            [
                a.id,
                a.student.full_name,
                a.student.email,
                a.status_label,
                "Oui" if a.cv_file else "Non",
                a.applied_at.strftime("%d/%m/%Y"),
            ]
        )

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=candidatures_{project_id}.csv"},
    )
