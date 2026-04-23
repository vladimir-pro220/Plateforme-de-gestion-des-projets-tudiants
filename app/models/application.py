"""
models/application.py
---------------------
Modèle Application : représente la candidature d'un étudiant à un projet.
Statuts : pending (en attente), accepted (accepté), rejected (refusé)
"""

from datetime import datetime
from app.extensions import db


class Application(db.Model):
    """Modèle candidature d'un étudiant à un projet."""

    __tablename__ = "applications"

    # Contrainte d'unicité : un étudiant ne peut postuler qu'une fois par projet
    __table_args__ = (db.UniqueConstraint("student_id", "project_id", name="uq_student_project"),)

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    motivation = db.Column(db.Text, nullable=False)
    cv_file = db.Column(db.String(200), nullable=True)  # Nom du fichier CV uploadé
    status = db.Column(db.String(20), default="pending", nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Propriétés calculées ─────────────────────────────────────────────────

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_accepted(self) -> bool:
        return self.status == "accepted"

    @property
    def is_rejected(self) -> bool:
        return self.status == "rejected"

    @property
    def status_badge(self) -> str:
        """Retourne la classe Bootstrap correspondant au statut."""
        badges = {
            "pending": "warning",
            "accepted": "success",
            "rejected": "danger",
        }
        return badges.get(self.status, "secondary")

    @property
    def status_label(self) -> str:
        """Retourne le libellé français du statut."""
        labels = {
            "pending": "En attente",
            "accepted": "Acceptée",
            "rejected": "Refusée",
        }
        return labels.get(self.status, self.status)

    def __repr__(self) -> str:
        return f"<Application student={self.student_id} project={self.project_id} [{self.status}]>"
