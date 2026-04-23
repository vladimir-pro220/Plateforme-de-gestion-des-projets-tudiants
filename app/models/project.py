"""
models/project.py
-----------------
Modèle Project : représente un sujet soumis par un enseignant.
Statuts : open (ouvert), closed (fermé), completed (terminé)
"""

from datetime import datetime
from app.extensions import db


class Project(db.Model):
    """Modèle projet soumis par un enseignant."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    max_students = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    applications = db.relationship(
        "Application",
        backref="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # ── Propriétés calculées ─────────────────────────────────────────────────

    @property
    def is_open(self) -> bool:
        return self.status == "open"

    @property
    def applications_count(self) -> int:
        """Nombre total de candidatures reçues."""
        return self.applications.count()

    @property
    def accepted_count(self) -> int:
        """Nombre de candidatures acceptées."""
        return self.applications.filter_by(status="accepted").count()

    @property
    def is_full(self) -> bool:
        """Vérifie si le projet a atteint son nombre max d'étudiants."""
        return self.accepted_count >= self.max_students

    @property
    def status_badge(self) -> str:
        """Retourne la classe Bootstrap correspondant au statut."""
        badges = {
            "open": "success",
            "closed": "danger",
            "completed": "secondary",
        }
        return badges.get(self.status, "secondary")

    @property
    def status_label(self) -> str:
        """Retourne le libellé français du statut."""
        labels = {
            "open": "Ouvert",
            "closed": "Fermé",
            "completed": "Terminé",
        }
        return labels.get(self.status, self.status)

    def __repr__(self) -> str:
        return f"<Project '{self.title}' [{self.status}]>"
