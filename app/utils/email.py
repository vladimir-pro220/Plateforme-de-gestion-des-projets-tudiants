"""
utils/email.py
--------------
Notifications email simulées.
En développement : les emails sont loggés dans la console.
En production : envoi réel via Flask-Mail (SMTP).
"""

import logging
from app.extensions import mail

logger = logging.getLogger(__name__)


def _log_email(to: str, subject: str, body: str) -> None:
    """Affiche l'email dans la console en mode développement."""
    logger.info("=" * 60)
    logger.info("📧 EMAIL SIMULÉ")
    logger.info(f"   À       : {to}")
    logger.info(f"   Sujet   : {subject}")
    logger.info(f"   Message : {body}")
    logger.info("=" * 60)


def notify_new_application(student_name: str, project_title: str, teacher_email: str) -> None:
    """
    Notifie l'enseignant qu'un étudiant vient de postuler à son projet.

    Args:
        student_name: Nom complet de l'étudiant
        project_title: Titre du projet concerné
        teacher_email: Email de l'enseignant à notifier
    """
    subject = f"Nouvelle candidature — {project_title}"
    body = (
        f"Bonjour,\n\n"
        f"L'étudiant(e) {student_name} vient de postuler à votre projet "
        f"« {project_title} ».\n\n"
        f"Connectez-vous à la plateforme pour consulter sa candidature.\n\n"
        f"Cordialement,\nLa plateforme Projets Étudiants"
    )

    _log_email(teacher_email, subject, body)

    try:
        from flask_mail import Message

        msg = Message(subject=subject, recipients=[teacher_email], body=body)
        mail.send(msg)
    except Exception as e:
        logger.warning(f"Envoi email échoué (mode dev) : {e}")


def notify_application_decision(student_email: str, project_title: str, decision: str) -> None:
    """
    Notifie l'étudiant de la décision sur sa candidature.

    Args:
        student_email: Email de l'étudiant
        project_title: Titre du projet
        decision: 'accepted' ou 'rejected'
    """
    if decision == "accepted":
        subject = f"Candidature acceptée — {project_title}"
        body = (
            f"Félicitations !\n\n"
            f"Votre candidature au projet « {project_title} » a été acceptée.\n\n"
            f"L'enseignant responsable vous contactera prochainement.\n\n"
            f"Cordialement,\nLa plateforme Projets Étudiants"
        )
    else:
        subject = f"Candidature non retenue — {project_title}"
        body = (
            f"Bonjour,\n\n"
            f"Nous vous informons que votre candidature au projet "
            f"« {project_title} » n'a pas été retenue.\n\n"
            f"D'autres projets sont disponibles sur la plateforme.\n\n"
            f"Cordialement,\nLa plateforme Projets Étudiants"
        )

    _log_email(student_email, subject, body)

    try:
        from flask_mail import Message

        msg = Message(subject=subject, recipients=[student_email], body=body)
        mail.send(msg)
    except Exception as e:
        logger.warning(f"Envoi email échoué (mode dev) : {e}")


def notify_registration(user_email: str, full_name: str, role: str) -> None:
    """
    Notifie l'utilisateur après son inscription.

    Args:
        user_email: Email du nouvel utilisateur
        full_name: Nom complet
        role: Rôle attribué
    """
    role_label = "Étudiant(e)" if role == "student" else "Enseignant(e)"
    subject = "Bienvenue sur la plateforme Projets Étudiants"
    body = (
        f"Bonjour {full_name},\n\n"
        f"Votre compte {role_label} a été créé avec succès.\n\n"
        f"Vous pouvez dès maintenant vous connecter et explorer "
        f"les projets disponibles.\n\n"
        f"Cordialement,\nLa plateforme Projets Étudiants"
    )

    _log_email(user_email, subject, body)

    try:
        from flask_mail import Message

        msg = Message(subject=subject, recipients=[user_email], body=body)
        mail.send(msg)
    except Exception as e:
        logger.warning(f"Envoi email échoué (mode dev) : {e}")
