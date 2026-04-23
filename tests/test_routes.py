"""
tests/test_routes.py
--------------------
Tests d'intégration des routes : codes HTTP, redirections, permissions.
Couvre toutes les routes principales de l'application.
"""

from app.models.application import Application

# ══════════════════════════════════════════════════════════════════════════
# TESTS ROUTES PUBLIQUES
# ══════════════════════════════════════════════════════════════════════════


class TestPublicRoutes:
    """Tests des routes accessibles sans authentification."""

    def test_home_page(self, client):
        """La page d'accueil retourne 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_projects_list(self, client):
        """La liste des projets retourne 200."""
        response = client.get("/projects/")
        assert response.status_code == 200

    def test_login_page(self, client):
        """La page de connexion retourne 200."""
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_register_page(self, client):
        """La page d'inscription retourne 200."""
        response = client.get("/auth/register")
        assert response.status_code == 200

    def test_project_detail_public(self, client, db, sample_project):
        """Le détail d'un projet est accessible publiquement."""
        response = client.get(f"/projects/{sample_project.id}")
        assert response.status_code == 200

    def test_unknown_route_404(self, client):
        """Une route inconnue retourne 404."""
        response = client.get("/route/inexistante/xyz")
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════
# TESTS ROUTES PROTÉGÉES (non connecté)
# ══════════════════════════════════════════════════════════════════════════


class TestProtectedRoutesUnauthenticated:
    """Tests des routes protégées sans authentification — doivent rediriger."""

    def test_dashboard_redirects(self, client):
        """Le dashboard redirige si non connecté."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302

    def test_project_create_redirects(self, client):
        """La création de projet redirige si non connecté."""
        response = client.get("/projects/create", follow_redirects=False)
        assert response.status_code == 302

    def test_apply_redirects(self, client, db, sample_project):
        """Postuler redirige si non connecté."""
        response = client.get(
            f"/applications/apply/{sample_project.id}",
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_my_applications_redirects(self, client):
        """Mes candidatures redirige si non connecté."""
        response = client.get("/applications/my", follow_redirects=False)
        assert response.status_code == 302

    def test_admin_users_redirects(self, client):
        """Le panel admin redirige si non connecté."""
        response = client.get("/admin/users", follow_redirects=False)
        assert response.status_code == 302

    def test_logout_redirects(self, client):
        """La déconnexion redirige si non connecté."""
        response = client.get("/auth/logout", follow_redirects=False)
        assert response.status_code == 302

    def test_export_redirects(self, client):
        """L'export CSV redirige si non connecté."""
        response = client.get("/export/projects.csv", follow_redirects=False)
        assert response.status_code == 302


# ══════════════════════════════════════════════════════════════════════════
# TESTS ROUTES ÉTUDIANT
# ══════════════════════════════════════════════════════════════════════════


class TestStudentRoutes:
    """Tests des routes accessibles pour un étudiant connecté."""

    def test_student_dashboard(self, client, db, student_user):
        """Un étudiant accède à son dashboard."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/dashboard/student", follow_redirects=True)
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_student_my_applications(self, client, db, student_user):
        """Un étudiant accède à ses candidatures."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/applications/my")
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_student_apply_page(self, client, db, student_user, sample_project):
        """Un étudiant accède au formulaire de candidature."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get(f"/applications/apply/{sample_project.id}")
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_student_apply_success(self, client, db, student_user, sample_project):
        """Un étudiant peut postuler à un projet ouvert."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            f"/applications/apply/{sample_project.id}",
            data={
                "motivation": "Je suis très motivé par ce projet et je possède "
                "toutes les compétences nécessaires pour le mener "
                "à bien dans les délais impartis.",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        app = Application.query.filter_by(
            student_id=student_user.id,
            project_id=sample_project.id,
        ).first()
        assert app is not None
        client.get("/auth/logout", follow_redirects=True)

    def test_student_cannot_apply_twice(self, client, db, student_user, sample_project):
        """Un étudiant ne peut pas postuler deux fois au même projet."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        # Première candidature
        client.post(
            f"/applications/apply/{sample_project.id}",
            data={
                "motivation": "Première candidature suffisamment longue pour passer la validation."
            },
            follow_redirects=True,
        )

        # Deuxième tentative
        response = client.post(
            f"/applications/apply/{sample_project.id}",
            data={"motivation": "Deuxième candidature au même projet."},
            follow_redirects=True,
        )
        assert response.status_code == 200
        count = Application.query.filter_by(
            student_id=student_user.id,
            project_id=sample_project.id,
        ).count()
        assert count == 1
        client.get("/auth/logout", follow_redirects=True)

    def test_student_cannot_create_project(self, client, db, student_user):
        """Un étudiant ne peut pas créer un projet."""
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


# ══════════════════════════════════════════════════════════════════════════
# TESTS ROUTES ENSEIGNANT
# ══════════════════════════════════════════════════════════════════════════


class TestTeacherRoutes:
    """Tests des routes accessibles pour un enseignant connecté."""

    def test_teacher_dashboard(self, client, db, teacher_user):
        """Un enseignant accède à son dashboard."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/dashboard/teacher", follow_redirects=True)
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_teacher_project_applications(self, client, db, teacher_user, sample_project):
        """Un enseignant accède aux candidatures de son projet."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get(f"/applications/project/{sample_project.id}")
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_teacher_export_csv(self, client, db, teacher_user):
        """Un enseignant peut exporter ses projets en CSV."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/export/projects.csv")
        assert response.status_code == 200
        assert "text/csv" in response.content_type
        client.get("/auth/logout", follow_redirects=True)

    def test_teacher_accept_application(self, client, db, teacher_user, sample_application):
        """Un enseignant peut accepter une candidature."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            f"/applications/{sample_application.id}/accept",
            follow_redirects=True,
        )
        assert response.status_code == 200
        updated = Application.query.get(sample_application.id)
        assert updated.status == "accepted"
        client.get("/auth/logout", follow_redirects=True)

    def test_teacher_reject_application(self, client, db, teacher_user, sample_application):
        """Un enseignant peut refuser une candidature."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            f"/applications/{sample_application.id}/reject",
            follow_redirects=True,
        )
        assert response.status_code == 200
        updated = Application.query.get(sample_application.id)
        assert updated.status == "rejected"
        client.get("/auth/logout", follow_redirects=True)

    def test_teacher_cannot_apply(self, client, db, teacher_user, sample_project):
        """Un enseignant ne peut pas postuler à un projet."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get(
            f"/applications/apply/{sample_project.id}",
            follow_redirects=False,
        )
        assert response.status_code in [302, 403]
        client.get("/auth/logout", follow_redirects=True)


# ══════════════════════════════════════════════════════════════════════════
# TESTS ROUTES ADMIN
# ══════════════════════════════════════════════════════════════════════════


class TestAdminRoutes:
    """Tests des routes accessibles pour un administrateur."""

    def test_admin_dashboard(self, client, db, admin_user):
        """Un admin accède à son dashboard."""
        client.post(
            "/auth/login",
            data={
                "email": admin_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/dashboard/admin", follow_redirects=True)
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_admin_users_list(self, client, db, admin_user):
        """Un admin accède à la liste des utilisateurs."""
        client.post(
            "/auth/login",
            data={
                "email": admin_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/admin/users")
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_admin_stats(self, client, db, admin_user):
        """Un admin accède aux statistiques."""
        client.post(
            "/auth/login",
            data={
                "email": admin_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/admin/stats")
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_admin_toggle_user(self, client, db, admin_user, student_user):
        """Un admin peut activer/désactiver un utilisateur."""
        client.post(
            "/auth/login",
            data={
                "email": admin_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        initial_status = student_user.is_active
        response = client.post(
            f"/admin/users/{student_user.id}/toggle",
            follow_redirects=True,
        )
        assert response.status_code == 200

        from app.models.user import User

        updated = User.query.get(student_user.id)
        assert updated.is_active != initial_status
        client.get("/auth/logout", follow_redirects=True)

    def test_admin_export_all_projects(self, client, db, admin_user):
        """Un admin peut exporter tous les projets en CSV."""
        client.post(
            "/auth/login",
            data={
                "email": admin_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/export/projects.csv")
        assert response.status_code == 200
        assert "text/csv" in response.content_type
        client.get("/auth/logout", follow_redirects=True)
