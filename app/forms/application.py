"""
forms/application.py
--------------------
Formulaire de candidature étudiant à un projet.
Inclut la lettre de motivation et l'upload du CV (PDF/DOC).
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class ApplicationForm(FlaskForm):
    """Formulaire de candidature avec motivation et CV."""

    motivation = TextAreaField(
        "Lettre de motivation",
        validators=[
            DataRequired(message="La lettre de motivation est obligatoire."),
            Length(
                min=50,
                max=2000,
                message="La motivation doit contenir entre 50 et 2000 caractères.",
            ),
        ],
    )
    cv_file = FileField(
        "CV (PDF ou Word — optionnel)",
        validators=[
            FileAllowed(
                ["pdf", "doc", "docx"],
                message="Seuls les fichiers PDF et Word sont acceptés.",
            ),
        ],
    )
    submit = SubmitField("Envoyer ma candidature")
