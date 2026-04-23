"""
tests/test_models.py
--------------------
Tests unitaires des modèles : User, Project, Application.
Vérifie la logique métier, les propriétés calculées et les contraintes DB.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.project import Project
from app.models.application import Application

# ══════════════════════════════════════════════════════════════════════════
# TESTS MODÈLE USER
# ══════════════════════════════════════════════════════════════════════════


class TestUserModel:
    """Tests unitaires du modèle User."""

    def test_create_user(self, db):
        """Un utilisateur peut être créé et sauvegardé en base."""
        user = User(
            email="test@example.com",
            first_name="Jean",
            last_name="Dupont",
            role="student",
        )
        user.set_password("motdepasse123")
        db.session.add(user)
        db.session.commit()

        saved = User.query.filter_by(email="test@example.com").first()
        assert saved is not None
        assert saved.first_name == "Jean"
        assert saved.role == "student"

    def test_password_is_hashed(self, db):
        """Le mot de passe ne doit jamais être stocké en clair."""
        user = User(
            email="hash@example.com",
            first_name="Alice",
            last_name="Martin",
            role="student",
        )
        user.set_password("motdepasse123")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "motdepasse123"
        assert len(user.password_hash) > 20

    def test_check_password_correct(self, student_user):
        """check_password retourne True pour le bon mot de passe."""
        assert student_user.check_password("password123") is True

    def test_check_password_wrong(self, student_user):
        """check_password retourne False pour un mauvais mot de passe."""
        assert student_user.check_password("mauvais_mdp") is False

    def test_full_name(self, student_user):
        """La propriété full_name retourne prénom + nom."""
        assert student_user.full_name == "Alice Durand"

    def test_role_student(self, student_user):
        """Les propriétés de rôle sont correctes pour un étudiant."""
        assert student_user.is_student is True
        assert student_user.is_teacher is False
        assert student_user.is_admin is False

    def test_role_teacher(self, teacher_user):
        """Les propriétés de rôle sont correctes pour un enseignant."""
        assert teacher_user.is_teacher is True
        assert teacher_user.is_student is False
        assert teacher_user.is_admin is False

    def test_role_admin(self, admin_user):
        """Les propriétés de rôle sont correctes pour un admin."""
        assert admin_user.is_admin is True
        assert admin_user.is_student is False
        assert admin_user.is_teacher is False

    def test_email_unique(self, db, student_user):
        """Deux utilisateurs ne peuvent pas avoir le même email."""
        duplicate = User(
            email=student_user.email,
            first_name="Bob",
            last_name="Test",
            role="student",
        )
        duplicate.set_password("password123")
        db.session.add(duplicate)
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_user_is_active_by_default(self, db):
        """Un utilisateur est actif par défaut."""
        user = User(
            email="actif@example.com",
            first_name="Test",
            last_name="User",
            role="student",
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        assert user.is_active is True

    def test_repr(self, student_user):
        """La représentation string du modèle est correcte."""
        assert "student@test.com" in repr(student_user)
        assert "student" in repr(student_user)


# ══════════════════════════════════════════════════════════════════════════
# TESTS MODÈLE PROJECT
# ══════════════════════════════════════════════════════════════════════════


class TestProjectModel:
    """Tests unitaires du modèle Project."""

    def test_create_project(self, db, teacher_user):
        """Un projet peut être créé et sauvegardé en base."""
        project = Project(
            title="Projet IA",
            description="Description du projet.",
            domain="Intelligence Artificielle",
            max_students=2,
            status="open",
            teacher_id=teacher_user.id,
        )
        db.session.add(project)
        db.session.commit()

        saved = Project.query.filter_by(title="Projet IA").first()
        assert saved is not None
        assert saved.domain == "Intelligence Artificielle"
        assert saved.max_students == 2

    def test_project_teacher_relation(self, sample_project, teacher_user):
        """Un projet est bien lié à son enseignant."""
        assert sample_project.teacher.id == teacher_user.id
        assert sample_project.teacher.full_name == teacher_user.full_name

    def test_is_open(self, sample_project):
        """is_open retourne True pour un projet ouvert."""
        assert sample_project.is_open is True

    def test_is_not_open_when_closed(self, db, teacher_user):
        """is_open retourne False pour un projet fermé."""
        project = Project(
            title="Projet Fermé",
            description="Description.",
            domain="Informatique",
            max_students=1,
            status="closed",
            teacher_id=teacher_user.id,
        )
        db.session.add(project)
        db.session.commit()
        assert project.is_open is False

    def test_status_label(self, db, teacher_user):
        """status_label retourne le bon libellé français."""
        statuses = {
            "open": "Ouvert",
            "closed": "Fermé",
            "completed": "Terminé",
        }
        for status, label in statuses.items():
            project = Project(
                title=f"Projet {status}",
                description="Test.",
                domain="Test",
                max_students=1,
                status=status,
                teacher_id=teacher_user.id,
            )
            db.session.add(project)
            db.session.commit()
            assert project.status_label == label

    def test_status_badge(self, sample_project):
        """status_badge retourne la bonne classe Bootstrap."""
        assert sample_project.status_badge == "success"

    def test_applications_count_empty(self, sample_project):
        """Un projet sans candidatures a un count de 0."""
        assert sample_project.applications_count == 0

    def test_applications_count(self, db, sample_project, student_user):
        """applications_count est correct après ajout d'une candidature."""
        app = Application(
            student_id=student_user.id,
            project_id=sample_project.id,
            motivation="Motivation de test suffisamment longue.",
            status="pending",
        )
        db.session.add(app)
        db.session.commit()
        assert sample_project.applications_count == 1

    def test_is_full(self, db, sample_project, student_user):
        """is_full retourne True quand le max d'étudiants est atteint."""
        # sample_project.max_students = 2, on accepte 2 candidatures
        student2 = User(
            email="student2@test.com",
            first_name="Bob",
            last_name="Test",
            role="student",
        )
        student2.set_password("password123")
        db.session.add(student2)
        db.session.flush()

        app1 = Application(
            student_id=student_user.id,
            project_id=sample_project.id,
            motivation="Motivation suffisamment longue pour le test.",
            status="accepted",
        )
        app2 = Application(
            student_id=student2.id,
            project_id=sample_project.id,
            motivation="Motivation suffisamment longue pour le test.",
            status="accepted",
        )
        db.session.add_all([app1, app2])
        db.session.commit()
        assert sample_project.is_full is True

    def test_repr(self, sample_project):
        """La représentation string du modèle est correcte."""
        assert "Projet Test IA" in repr(sample_project)
        assert "open" in repr(sample_project)


# ══════════════════════════════════════════════════════════════════════════
# TESTS MODÈLE APPLICATION
# ══════════════════════════════════════════════════════════════════════════


class TestApplicationModel:
    """Tests unitaires du modèle Application."""

    def test_create_application(self, db, student_user, sample_project):
        """Une candidature peut être créée et sauvegardée en base."""
        application = Application(
            student_id=student_user.id,
            project_id=sample_project.id,
            motivation="Je suis très motivé par ce projet de recherche.",
            status="pending",
        )
        db.session.add(application)
        db.session.commit()

        saved = Application.query.filter_by(
            student_id=student_user.id,
            project_id=sample_project.id,
        ).first()
        assert saved is not None
        assert saved.status == "pending"

    def test_application_relations(self, sample_application, student_user, sample_project):
        """Une candidature est bien liée à l'étudiant et au projet."""
        assert sample_application.student.id == student_user.id
        assert sample_application.project.id == sample_project.id

    def test_is_pending(self, sample_application):
        """is_pending retourne True pour une candidature en attente."""
        assert sample_application.is_pending is True
        assert sample_application.is_accepted is False
        assert sample_application.is_rejected is False

    def test_is_accepted(self, db, sample_application):
        """is_accepted retourne True pour une candidature acceptée."""
        sample_application.status = "accepted"
        db.session.commit()
        assert sample_application.is_accepted is True
        assert sample_application.is_pending is False

    def test_is_rejected(self, db, sample_application):
        """is_rejected retourne True pour une candidature refusée."""
        sample_application.status = "rejected"
        db.session.commit()
        assert sample_application.is_rejected is True

    def test_status_label(self, sample_application):
        """status_label retourne le bon libellé français."""
        assert sample_application.status_label == "En attente"

    def test_status_badge(self, sample_application):
        """status_badge retourne la bonne classe Bootstrap."""
        assert sample_application.status_badge == "warning"

    def test_unique_constraint(self, db, sample_application, student_user, sample_project):
        """Un étudiant ne peut pas postuler deux fois au même projet."""
        duplicate = Application(
            student_id=student_user.id,
            project_id=sample_project.id,
            motivation="Deuxième candidature au même projet.",
            status="pending",
        )
        db.session.add(duplicate)
        with pytest.raises(IntegrityError):
            db.session.commit()

    def test_repr(self, sample_application, student_user, sample_project):
        """La représentation string du modèle est correcte."""
        r = repr(sample_application)
        assert str(student_user.id) in r
        assert str(sample_project.id) in r
        assert "pending" in r
