"""
forms/__init__.py
-----------------
Expose tous les formulaires pour un accès simplifié.
Usage : from app.forms import LoginForm, RegisterForm, ProjectForm
"""

from app.forms.auth import LoginForm, RegisterForm
from app.forms.project import ProjectForm, DOMAINS
from app.forms.application import ApplicationForm

__all__ = ["LoginForm", "RegisterForm", "ProjectForm", "ApplicationForm", "DOMAINS"]
