"""
models/__init__.py
------------------
Expose tous les modèles pour un accès simplifié.
Usage : from app.models import User, Project, Application
"""

from app.models.user import User
from app.models.project import Project
from app.models.application import Application

__all__ = ["User", "Project", "Application"]
