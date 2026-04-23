"""
routes/projects.py
------------------
Blueprint projets : liste publique, détail, CRUD enseignants.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.project import Project
from app.models.application import Application
from app.forms.project import ProjectForm
from app.utils.decorators import teacher_required

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


@projects_bp.route("/")
def list():
    """Liste publique des projets avec recherche, filtres et pagination."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    domain = request.args.get("domain", "")
    status = request.args.get("status", "open")

    query = Project.query

    if search:
        query = query.filter(Project.title.ilike(f"%{search}%"))
    if domain:
        query = query.filter_by(domain=domain)
    if status:
        query = query.filter_by(status=status)

    query = query.order_by(Project.created_at.desc())
    projects = query.paginate(page=page, per_page=10, error_out=False)

    # Domaines distincts pour le filtre
    domains = db.session.query(Project.domain).distinct().all()
    domains = [d[0] for d in domains]

    return render_template(
        "projects/list.html",
        projects=projects,
        search=search,
        domain=domain,
        status=status,
        domains=domains,
        title="Projets disponibles",
    )


@projects_bp.route("/<int:project_id>")
def detail(project_id):
    """Détail d'un projet."""
    project = Project.query.get_or_404(project_id)

    # Vérifie si l'étudiant connecté a déjà postulé
    user_application = None
    if current_user.is_authenticated and current_user.is_student:
        user_application = Application.query.filter_by(
            student_id=current_user.id,
            project_id=project_id,
        ).first()

    return render_template(
        "projects/detail.html",
        project=project,
        user_application=user_application,
        title=project.title,
    )


@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
@teacher_required
def create():
    """Création d'un nouveau projet (enseignant uniquement)."""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            domain=form.domain.data,
            max_students=form.max_students.data,
            status=form.status.data,
            teacher_id=current_user.id,
        )
        db.session.add(project)
        db.session.commit()
        flash("Projet créé avec succès !", "success")
        return redirect(url_for("projects.detail", project_id=project.id))

    return render_template("projects/create.html", form=form, title="Créer un projet")


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def edit(project_id):
    """Modification d'un projet (enseignant propriétaire uniquement)."""
    project = Project.query.get_or_404(project_id)

    if project.teacher_id != current_user.id:
        abort(403)

    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.domain = form.domain.data
        project.max_students = form.max_students.data
        project.status = form.status.data
        db.session.commit()
        flash("Projet mis à jour avec succès !", "success")
        return redirect(url_for("projects.detail", project_id=project.id))

    return render_template(
        "projects/edit.html", form=form, project=project, title="Modifier le projet"
    )


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete(project_id):
    """Suppression d'un projet (enseignant propriétaire uniquement)."""
    project = Project.query.get_or_404(project_id)

    if project.teacher_id != current_user.id:
        abort(403)

    db.session.delete(project)
    db.session.commit()
    flash("Projet supprimé.", "info")
    return redirect(url_for("dashboard.index"))
