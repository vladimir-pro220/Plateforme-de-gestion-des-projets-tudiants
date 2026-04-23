"""
routes/applications.py
----------------------
Blueprint candidatures : postuler, voir, accepter, refuser.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.project import Project
from app.models.application import Application
from app.forms.application import ApplicationForm
from app.utils.decorators import student_required, teacher_required
from app.utils.helpers import allowed_file, save_file
from app.utils.email import notify_new_application, notify_application_decision

applications_bp = Blueprint("applications", __name__, url_prefix="/applications")


@applications_bp.route("/apply/<int:project_id>", methods=["GET", "POST"])
@login_required
@student_required
def apply(project_id):
    """Formulaire de candidature à un projet (étudiant uniquement)."""
    project = Project.query.get_or_404(project_id)

    if not project.is_open:
        flash("Ce projet n'accepte plus de candidatures.", "warning")
        return redirect(url_for("projects.detail", project_id=project_id))

    if project.is_full:
        flash("Ce projet a atteint son nombre maximum d'étudiants.", "warning")
        return redirect(url_for("projects.detail", project_id=project_id))

    # Vérifier si déjà candidat
    existing = Application.query.filter_by(
        student_id=current_user.id, project_id=project_id
    ).first()
    if existing:
        flash("Vous avez déjà postulé à ce projet.", "warning")
        return redirect(url_for("projects.detail", project_id=project_id))

    form = ApplicationForm()
    if form.validate_on_submit():
        cv_filename = None
        if form.cv_file.data and form.cv_file.data.filename:
            if allowed_file(form.cv_file.data.filename):
                cv_filename = save_file(form.cv_file.data, subfolder="cvs")
            else:
                flash("Format de fichier non autorisé.", "danger")
                return render_template("applications/apply.html", form=form, project=project)

        application = Application(
            student_id=current_user.id,
            project_id=project_id,
            motivation=form.motivation.data,
            cv_file=cv_filename,
        )
        db.session.add(application)
        db.session.commit()

        # Notification email à l'enseignant
        notify_new_application(
            student_name=current_user.full_name,
            project_title=project.title,
            teacher_email=project.teacher.email,
        )

        flash("Candidature envoyée avec succès !", "success")
        return redirect(url_for("applications.my_applications"))

    return render_template(
        "applications/apply.html", form=form, project=project, title="Postuler au projet"
    )


@applications_bp.route("/my")
@login_required
@student_required
def my_applications():
    """Liste des candidatures de l'étudiant connecté."""
    applications = (
        Application.query.filter_by(student_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    return render_template(
        "applications/my_applications.html",
        applications=applications,
        title="Mes candidatures",
    )


@applications_bp.route("/project/<int:project_id>")
@login_required
@teacher_required
def project_applications(project_id):
    """Liste des candidatures reçues pour un projet (enseignant)."""
    project = Project.query.get_or_404(project_id)

    if project.teacher_id != current_user.id:
        abort(403)

    status_filter = request.args.get("status", "")
    query = Application.query.filter_by(project_id=project_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    applications = query.order_by(Application.applied_at.desc()).all()

    return render_template(
        "applications/list.html",
        applications=applications,
        project=project,
        status_filter=status_filter,
        title=f"Candidatures — {project.title}",
    )


@applications_bp.route("/<int:app_id>/accept", methods=["POST"])
@login_required
@teacher_required
def accept(app_id):
    """Accepter une candidature."""
    application = Application.query.get_or_404(app_id)

    if application.project.teacher_id != current_user.id:
        abort(403)

    application.status = "accepted"
    db.session.commit()

    notify_application_decision(
        student_email=application.student.email,
        project_title=application.project.title,
        decision="accepted",
    )

    flash(f"Candidature de {application.student.full_name} acceptée.", "success")
    return redirect(url_for("applications.project_applications", project_id=application.project_id))


@applications_bp.route("/<int:app_id>/reject", methods=["POST"])
@login_required
@teacher_required
def reject(app_id):
    """Refuser une candidature."""
    application = Application.query.get_or_404(app_id)

    if application.project.teacher_id != current_user.id:
        abort(403)

    application.status = "rejected"
    db.session.commit()

    notify_application_decision(
        student_email=application.student.email,
        project_title=application.project.title,
        decision="rejected",
    )

    flash(f"Candidature de {application.student.full_name} refusée.", "info")
    return redirect(url_for("applications.project_applications", project_id=application.project_id))
