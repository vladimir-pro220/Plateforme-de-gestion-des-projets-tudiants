"""
routes/auth.py
--------------
Blueprint authentification : inscription, connexion, déconnexion.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.forms.auth import LoginForm, RegisterForm
from app.utils.email import notify_registration

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Votre compte a été désactivé. Contactez l'administrateur.", "danger")
                return redirect(url_for("auth.login"))
            login_user(user, remember=form.remember_me.data)
            flash(f"Bienvenue, {user.first_name} !", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Email ou mot de passe incorrect.", "danger")

    return render_template("auth/login.html", form=form, title="Connexion")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Page d'inscription."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        notify_registration(user.email, user.full_name, user.role)
        flash("Compte créé avec succès ! Vous pouvez vous connecter.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form, title="Inscription")


@auth_bp.route("/logout")
@login_required
def logout():
    """Déconnexion de l'utilisateur."""
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login"))
