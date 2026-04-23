"""
utils/helpers.py
----------------
Fonctions utilitaires réutilisables dans tout le projet.
Pagination, upload de fichiers, statistiques globales, formatage.
"""

import os
import uuid
from datetime import datetime
from flask import current_app

# ── Upload de fichiers ────────────────────────────────────────────────────────


def allowed_file(filename: str) -> bool:
    """
    Vérifie que l'extension du fichier est autorisée.

    Args:
        filename: Nom du fichier à vérifier

    Returns:
        bool: True si l'extension est autorisée
    """
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "doc", "docx"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def save_file(file, subfolder: str = "") -> str:
    """
    Sauvegarde un fichier uploadé avec un nom unique.

    Args:
        file: Objet fichier Flask (request.files)
        subfolder: Sous-dossier optionnel dans uploads/

    Returns:
        str: Nom du fichier sauvegardé
    """
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_path = current_app.config["UPLOAD_FOLDER"]
    if subfolder:
        upload_path = os.path.join(upload_path, subfolder)
        os.makedirs(upload_path, exist_ok=True)

    file.save(os.path.join(upload_path, unique_name))
    return unique_name


# ── Statistiques globales ─────────────────────────────────────────────────────


def get_global_stats() -> dict:
    """
    Retourne les statistiques globales de la plateforme.
    Utilisé dans le dashboard admin et la page d'accueil.

    Returns:
        dict: Dictionnaire de statistiques
    """
    from app.models import User, Project, Application

    total_users = User.query.count()
    total_students = User.query.filter_by(role="student").count()
    total_teachers = User.query.filter_by(role="teacher").count()
    total_projects = Project.query.count()
    open_projects = Project.query.filter_by(status="open").count()
    total_applications = Application.query.count()
    accepted_applications = Application.query.filter_by(status="accepted").count()

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_projects": total_projects,
        "open_projects": open_projects,
        "total_applications": total_applications,
        "accepted_applications": accepted_applications,
    }


def get_teacher_stats(teacher_id: int) -> dict:
    """
    Retourne les statistiques d'un enseignant.

    Args:
        teacher_id: ID de l'enseignant

    Returns:
        dict: Statistiques de l'enseignant
    """
    from app.models import Project, Application

    my_projects = Project.query.filter_by(teacher_id=teacher_id).count()
    open_projects = Project.query.filter_by(teacher_id=teacher_id, status="open").count()

    project_ids = [p.id for p in Project.query.filter_by(teacher_id=teacher_id).all()]
    total_applications = Application.query.filter(Application.project_id.in_(project_ids)).count()
    pending_applications = Application.query.filter(
        Application.project_id.in_(project_ids),
        Application.status == "pending",
    ).count()

    return {
        "my_projects": my_projects,
        "open_projects": open_projects,
        "total_applications": total_applications,
        "pending_applications": pending_applications,
    }


def get_student_stats(student_id: int) -> dict:
    """
    Retourne les statistiques d'un étudiant.

    Args:
        student_id: ID de l'étudiant

    Returns:
        dict: Statistiques de l'étudiant
    """
    from app.models import Application

    total = Application.query.filter_by(student_id=student_id).count()
    pending = Application.query.filter_by(student_id=student_id, status="pending").count()
    accepted = Application.query.filter_by(student_id=student_id, status="accepted").count()
    rejected = Application.query.filter_by(student_id=student_id, status="rejected").count()

    return {
        "total_applications": total,
        "pending": pending,
        "accepted": accepted,
        "rejected": rejected,
    }


# ── Formatage ─────────────────────────────────────────────────────────────────


def format_date(dt: datetime, fmt: str = "%d/%m/%Y") -> str:
    """
    Formate une date en français.

    Args:
        dt: Objet datetime
        fmt: Format de date souhaité

    Returns:
        str: Date formatée
    """
    if not dt:
        return "—"
    return dt.strftime(fmt)
