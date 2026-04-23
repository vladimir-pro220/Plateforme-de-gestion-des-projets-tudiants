"""
models/user.py
--------------
Modèle User : représente tous les utilisateurs de la plateforme.
Rôles possibles : student, teacher, admin
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """Modèle utilisateur avec gestion des rôles."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    projects = db.relationship(
        "Project",
        backref="teacher",
        lazy="dynamic",
        foreign_keys="Project.teacher_id",
    )
    applications = db.relationship(
        "Application",
        backref="student",
        lazy="dynamic",
        foreign_keys="Application.student_id",
    )

    # ── Mot de passe ─────────────────────────────────────────────────────────

    def set_password(self, password: str) -> None:
        """Hash et stocke le mot de passe."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe fourni contre le hash stocké."""
        return check_password_hash(self.password_hash, password)

    # ── Rôles ────────────────────────────────────────────────────────────────

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    # ── Utilitaires ──────────────────────────────────────────────────────────

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"


@login_manager.user_loader
def load_user(user_id: int):
    """Callback Flask-Login : charge l'utilisateur depuis la session."""
    return User.query.get(int(user_id))
