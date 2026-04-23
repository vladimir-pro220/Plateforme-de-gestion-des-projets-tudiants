"""
tests/conftest.py
-----------------
Fixtures pytest : application de test, client HTTP, base de données en mémoire.
Partagées automatiquement par tous les fichiers de test.
"""

import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.project import Project
from app.models.application import Application


# ── Application de test ─────────────────────────────────────────────────
@pytest.fixture(scope="session")
def app():
    """Crée une instance Flask configurée pour les tests."""
    app = create_app("testing")

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


# ── Client HTTP ─────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def client(app):
    """Client HTTP Flask pour simuler les requêtes."""
    return app.test_client()


# ── Base de données ─────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def db(app):
    """
    Fournit une session DB propre pour chaque test.
    Toutes les données sont supprimées après chaque test.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
        _db.create_all()


# ── Utilisateurs de test ─────────────────────────────────────────────────
@pytest.fixture
def admin_user(db):
    """Crée un utilisateur admin de test."""
    user = User(
        email="admin@test.com",
        first_name="Super",
        last_name="Admin",
        role="admin",
        is_active=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def teacher_user(db):
    """Crée un utilisateur enseignant de test."""
    user = User(
        email="teacher@test.com",
        first_name="Jean",
        last_name="Dupont",
        role="teacher",
        is_active=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def student_user(db):
    """Crée un utilisateur étudiant de test."""
    user = User(
        email="student@test.com",
        first_name="Alice",
        last_name="Durand",
        role="student",
        is_active=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


# ── Projet de test ───────────────────────────────────────────────────────
@pytest.fixture
def sample_project(db, teacher_user):
    """Crée un projet de test associé à l'enseignant."""
    project = Project(
        title="Projet Test IA",
        description="Description du projet de test en intelligence artificielle.",
        domain="Intelligence Artificielle",
        max_students=2,
        status="open",
        teacher_id=teacher_user.id,
    )
    db.session.add(project)
    db.session.commit()
    return project


# ── Candidature de test ──────────────────────────────────────────────────
@pytest.fixture
def sample_application(db, student_user, sample_project):
    """Crée une candidature de test."""
    application = Application(
        student_id=student_user.id,
        project_id=sample_project.id,
        motivation="Je suis très motivé par ce projet et je possède les compétences requises.",
        status="pending",
    )
    db.session.add(application)
    db.session.commit()
    return application


# ── Helpers connexion ────────────────────────────────────────────────────
@pytest.fixture
def logged_student(client, student_user):
    """Client HTTP avec un étudiant connecté."""
    client.post(
        "/auth/login",
        data={
            "email": student_user.email,
            "password": "password123",
        },
        follow_redirects=True,
    )
    yield client
    client.get("/auth/logout", follow_redirects=True)


@pytest.fixture
def logged_teacher(client, teacher_user):
    """Client HTTP avec un enseignant connecté."""
    client.post(
        "/auth/login",
        data={
            "email": teacher_user.email,
            "password": "password123",
        },
        follow_redirects=True,
    )
    yield client
    client.get("/auth/logout", follow_redirects=True)


@pytest.fixture
def logged_admin(client, admin_user):
    """Client HTTP avec un admin connecté."""
    client.post(
        "/auth/login",
        data={
            "email": admin_user.email,
            "password": "password123",
        },
        follow_redirects=True,
    )
    yield client
    client.get("/auth/logout", follow_redirects=True)
