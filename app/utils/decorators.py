"""
utils/decorators.py
-------------------
Décorateurs personnalisés pour la protection des routes par rôle.
Utilisés au-dessus des fonctions de vue dans les blueprints.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """
    Décorateur générique : autorise uniquement les rôles spécifiés.

    Usage :
        @role_required('teacher', 'admin')
        def ma_vue():
            ...
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Veuillez vous connecter pour accéder à cette page.", "warning")
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def student_required(f):
    """
    Décorateur : autorise uniquement les étudiants.

    Usage :
        @student_required
        def ma_vue():
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_student:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def teacher_required(f):
    """
    Décorateur : autorise uniquement les enseignants.

    Usage :
        @teacher_required
        def ma_vue():
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_teacher:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Décorateur : autorise uniquement les administrateurs.

    Usage :
        @admin_required
        def ma_vue():
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
