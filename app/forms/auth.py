"""
forms/auth.py
-------------
Formulaires d'authentification : connexion et inscription.
Validation côté serveur avec WTForms + protection CSRF Flask-WTF.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    """Formulaire de connexion."""

    email = StringField(
        "Adresse email",
        validators=[
            DataRequired(message="L'email est obligatoire."),
            Email(message="Adresse email invalide."),
        ],
    )
    password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired(message="Le mot de passe est obligatoire."),
        ],
    )
    remember_me = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")


class RegisterForm(FlaskForm):
    """Formulaire d'inscription avec choix du rôle."""

    first_name = StringField(
        "Prénom",
        validators=[
            DataRequired(message="Le prénom est obligatoire."),
            Length(min=2, max=50, message="Le prénom doit contenir entre 2 et 50 caractères."),
        ],
    )
    last_name = StringField(
        "Nom",
        validators=[
            DataRequired(message="Le nom est obligatoire."),
            Length(min=2, max=50, message="Le nom doit contenir entre 2 et 50 caractères."),
        ],
    )
    email = StringField(
        "Adresse email",
        validators=[
            DataRequired(message="L'email est obligatoire."),
            Email(message="Adresse email invalide."),
            Length(max=120, message="L'email ne peut pas dépasser 120 caractères."),
        ],
    )
    role = SelectField(
        "Je suis",
        choices=[
            ("student", "Étudiant(e)"),
            ("teacher", "Enseignant(e)"),
        ],
        validators=[DataRequired(message="Veuillez choisir un rôle.")],
    )
    password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired(message="Le mot de passe est obligatoire."),
            Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(message="La confirmation est obligatoire."),
            EqualTo("password", message="Les mots de passe ne correspondent pas."),
        ],
    )
    submit = SubmitField("S'inscrire")

    def validate_email(self, field):
        """Vérifie que l'email n'est pas déjà utilisé."""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Cette adresse email est déjà utilisée.")
