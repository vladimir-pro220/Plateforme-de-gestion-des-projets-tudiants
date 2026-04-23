"""
tests/test_auth.py
------------------
Tests d'intégration : inscription, connexion, déconnexion, rôles, accès refusé.
"""

from app.models.user import User

# ══════════════════════════════════════════════════════════════════════════
# TESTS INSCRIPTION
# ══════════════════════════════════════════════════════════════════════════


class TestRegister:
    """Tests de la route /auth/register."""

    def test_register_page_loads(self, client):
        """La page d'inscription se charge correctement."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert "Inscription" in response.data.decode("utf-8")

    def test_register_success(self, client, db):
        """Un nouvel utilisateur peut s'inscrire avec des données valides."""
        response = client.post(
            "/auth/register",
            data={
                "first_name": "Paul",
                "last_name": "Test",
                "email": "paul@test.com",
                "role": "student",
                "password": "password123",
                "password2": "password123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        user = User.query.filter_by(email="paul@test.com").first()
        assert user is not None
        assert user.first_name == "Paul"
        assert user.role == "student"

    def test_register_duplicate_email(self, client, db, student_user):
        """L'inscription échoue si l'email est déjà utilisé."""
        response = client.post(
            "/auth/register",
            data={
                "first_name": "Autre",
                "last_name": "User",
                "email": student_user.email,
                "role": "student",
                "password": "password123",
                "password2": "password123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        # Deux utilisateurs avec le même email ne doivent pas exister
        count = User.query.filter_by(email=student_user.email).count()
        assert count == 1

    def test_register_password_mismatch(self, client, db):
        """L'inscription échoue si les mots de passe ne correspondent pas."""
        response = client.post(
            "/auth/register",
            data={
                "first_name": "Test",
                "last_name": "User",
                "email": "mismatch@test.com",
                "role": "student",
                "password": "password123",
                "password2": "different456",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        user = User.query.filter_by(email="mismatch@test.com").first()
        assert user is None

    def test_register_missing_fields(self, client, db):
        """L'inscription échoue si des champs obligatoires sont manquants."""
        response = client.post(
            "/auth/register",
            data={
                "email": "",
                "password": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200

    def test_register_redirects_authenticated(self, client, db, student_user):
        """Un utilisateur déjà connecté est redirigé depuis /register."""
        # Connexion
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/auth/register", follow_redirects=False)
        assert response.status_code == 302
        client.get("/auth/logout", follow_redirects=True)


# ══════════════════════════════════════════════════════════════════════════
# TESTS CONNEXION
# ══════════════════════════════════════════════════════════════════════════


class TestLogin:
    """Tests de la route /auth/login."""

    def test_login_page_loads(self, client):
        """La page de connexion se charge correctement."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert "Connexion" in response.data.decode("utf-8")

    def test_login_success_student(self, client, db, student_user):
        """Un étudiant peut se connecter avec les bons identifiants."""
        response = client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert student_user.first_name.encode() in response.data
        client.get("/auth/logout", follow_redirects=True)

    def test_login_success_teacher(self, client, db, teacher_user):
        """Un enseignant peut se connecter avec les bons identifiants."""
        response = client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_login_wrong_password(self, client, db, student_user):
        """La connexion échoue avec un mauvais mot de passe."""
        response = client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "mauvais_mdp",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "incorrect" in response.data.decode(
            "utf-8"
        ).lower() or "danger" in response.data.decode("utf-8")

    def test_login_wrong_email(self, client, db):
        """La connexion échoue avec un email inexistant."""
        response = client.post(
            "/auth/login",
            data={
                "email": "inexistant@test.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "incorrect" in response.data.decode(
            "utf-8"
        ).lower() or "danger" in response.data.decode("utf-8")

    def test_login_inactive_user(self, client, db, student_user):
        """La connexion échoue pour un compte désactivé."""
        student_user.is_active = False
        db.session.commit()

        response = client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "désactivé" in response.data.decode("utf-8") or "danger" in response.data.decode(
            "utf-8"
        )

        # Réactive pour ne pas affecter d'autres tests
        student_user.is_active = True
        db.session.commit()

    def test_login_redirects_authenticated(self, client, db, student_user):
        """Un utilisateur déjà connecté est redirigé depuis /login."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/auth/login", follow_redirects=False)
        assert response.status_code == 302
        client.get("/auth/logout", follow_redirects=True)


# ══════════════════════════════════════════════════════════════════════════
# TESTS DÉCONNEXION
# ══════════════════════════════════════════════════════════════════════════


class TestLogout:
    """Tests de la route /auth/logout."""

    def test_logout_success(self, client, db, student_user):
        """Un utilisateur connecté peut se déconnecter."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/auth/logout", follow_redirects=True)
        assert response.status_code == 200
        assert "déconnecté" in response.data.decode("utf-8") or "Connexion" in response.data.decode(
            "utf-8"
        )

    def test_logout_requires_login(self, client):
        """La déconnexion redirige si l'utilisateur n'est pas connecté."""
        response = client.get("/auth/logout", follow_redirects=False)
        assert response.status_code == 302


# ══════════════════════════════════════════════════════════════════════════
# TESTS CONTRÔLE D'ACCÈS PAR RÔLE
# ══════════════════════════════════════════════════════════════════════════


class TestRoleAccess:
    """Tests de contrôle d'accès selon le rôle."""

    def test_student_cannot_access_admin(self, client, db, student_user):
        """Un étudiant ne peut pas accéder au panel admin."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/admin/users", follow_redirects=False)
        assert response.status_code in [302, 403]
        client.get("/auth/logout", follow_redirects=True)

    def test_teacher_cannot_access_admin(self, client, db, teacher_user):
        """Un enseignant ne peut pas accéder au panel admin."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/admin/users", follow_redirects=False)
        assert response.status_code in [302, 403]
        client.get("/auth/logout", follow_redirects=True)

    def test_admin_can_access_admin(self, client, db, admin_user):
        """Un admin peut accéder au panel admin."""
        client.post(
            "/auth/login",
            data={
                "email": admin_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/admin/users", follow_redirects=True)
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_student_cannot_create_project(self, client, db, student_user):
        """Un étudiant ne peut pas accéder à la création de projet."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/projects/create", follow_redirects=False)
        assert response.status_code in [302, 403]
        client.get("/auth/logout", follow_redirects=True)

    def test_unauthenticated_cannot_access_dashboard(self, client):
        """Un utilisateur non connecté est redirigé depuis le dashboard."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
