"""
forms/project.py
----------------
Formulaire de création et modification de projet.
Réservé aux enseignants uniquement.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

# Domaines disponibles pour les projets
DOMAINS = [
    ("", "-- Choisir un domaine --"),
    ("informatique", "Informatique"),
    ("reseaux", "Réseaux & Télécommunications"),
    ("ia", "Intelligence Artificielle"),
    ("web", "Développement Web"),
    ("mobile", "Développement Mobile"),
    ("securite", "Cybersécurité"),
    ("data", "Data Science & Big Data"),
    ("systemes", "Systèmes Embarqués"),
    ("gestion", "Gestion & Management"),
    ("autre", "Autre"),
]


class ProjectForm(FlaskForm):
    """Formulaire de création et d'édition de projet."""

    title = StringField(
        "Titre du projet",
        validators=[
            DataRequired(message="Le titre est obligatoire."),
            Length(min=5, max=200, message="Le titre doit contenir entre 5 et 200 caractères."),
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(message="La description est obligatoire."),
            Length(min=20, message="La description doit contenir au moins 20 caractères."),
        ],
    )
    domain = SelectField(
        "Domaine",
        choices=DOMAINS,
        validators=[DataRequired(message="Veuillez choisir un domaine.")],
    )
    max_students = IntegerField(
        "Nombre maximum d'étudiants",
        default=1,
        validators=[
            DataRequired(message="Ce champ est obligatoire."),
            NumberRange(min=1, max=10, message="Le nombre d'étudiants doit être entre 1 et 10."),
        ],
    )
    status = SelectField(
        "Statut",
        choices=[
            ("open", "Ouvert"),
            ("closed", "Fermé"),
            ("completed", "Terminé"),
        ],
        default="open",
        validators=[DataRequired()],
    )
    submit = SubmitField("Enregistrer")
