"""
tests/test_projects.py
----------------------
Tests d'intégration : CRUD projets, droits enseignant vs étudiant.
"""

from app.models.project import Project

# ══════════════════════════════════════════════════════════════════════════
# TESTS LISTE PROJETS
# ══════════════════════════════════════════════════════════════════════════


class TestProjectList:
    """Tests de la route GET /projects/."""

    def test_list_accessible_public(self, client):
        """La liste des projets est accessible sans être connecté."""
        response = client.get("/projects/")
        assert response.status_code == 200

    def test_list_shows_projects(self, client, db, sample_project):
        """La liste affiche bien les projets existants."""
        response = client.get("/projects/")
        assert response.status_code == 200
        assert sample_project.title.encode() in response.data

    def test_list_search_filter(self, client, db, sample_project):
        """La recherche par titre filtre correctement les projets."""
        response = client.get("/projects/?search=Projet+Test")
        assert response.status_code == 200
        assert sample_project.title.encode() in response.data

    def test_list_search_no_results(self, client, db, sample_project):
        """Une recherche sans résultats affiche un message approprié."""
        response = client.get("/projects/?search=xyzabc123inexistant")
        assert response.status_code == 200

    def test_list_domain_filter(self, client, db, sample_project):
        """Le filtre par domaine fonctionne correctement."""
        response = client.get(f"/projects/?domain={sample_project.domain}")
        assert response.status_code == 200
        assert sample_project.title.encode() in response.data

    def test_list_status_filter(self, client, db, sample_project):
        """Le filtre par statut fonctionne correctement."""
        response = client.get("/projects/?status=open")
        assert response.status_code == 200
        assert sample_project.title.encode() in response.data

    def test_list_pagination(self, client, db, teacher_user):
        """La pagination fonctionne correctement."""
        for i in range(12):
            p = Project(
                title=f"Projet Pagination {i}",
                description="Description de test.",
                domain="informatique",
                max_students=1,
                status="open",
                teacher_id=teacher_user.id,
            )
            db.session.add(p)
        db.session.commit()

        response = client.get("/projects/?page=1")
        assert response.status_code == 200

        response2 = client.get("/projects/?page=2")
        assert response2.status_code == 200


# ══════════════════════════════════════════════════════════════════════════
# TESTS DÉTAIL PROJET
# ══════════════════════════════════════════════════════════════════════════


class TestProjectDetail:
    """Tests de la route GET /projects/<id>."""

    def test_detail_accessible_public(self, client, db, sample_project):
        """Le détail d'un projet est accessible sans être connecté."""
        response = client.get(f"/projects/{sample_project.id}")
        assert response.status_code == 200

    def test_detail_shows_project_info(self, client, db, sample_project):
        """Le détail affiche bien les informations du projet."""
        response = client.get(f"/projects/{sample_project.id}")
        assert response.status_code == 200
        assert sample_project.title.encode() in response.data
        assert sample_project.domain.encode() in response.data

    def test_detail_404_for_unknown(self, client):
        """Une 404 est retournée pour un projet inexistant."""
        response = client.get("/projects/99999")
        assert response.status_code == 404

    def test_detail_shows_apply_button_for_student(self, client, db, student_user, sample_project):
        """Le bouton postuler est visible pour un étudiant connecté."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get(f"/projects/{sample_project.id}")
        assert response.status_code == 200
        assert "Postuler" in response.data.decode("utf-8")
        client.get("/auth/logout", follow_redirects=True)

    def test_detail_shows_edit_button_for_owner(self, client, db, teacher_user, sample_project):
        """Le bouton modifier est visible pour l'enseignant propriétaire."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get(f"/projects/{sample_project.id}")
        assert response.status_code == 200
        assert "Modifier" in response.data.decode("utf-8")
        client.get("/auth/logout", follow_redirects=True)


# ══════════════════════════════════════════════════════════════════════════
# TESTS CRÉATION PROJET
# ══════════════════════════════════════════════════════════════════════════


class TestProjectCreate:
    """Tests de la route /projects/create."""

    def test_create_page_requires_login(self, client):
        """La page de création redirige si non connecté."""
        response = client.get("/projects/create", follow_redirects=False)
        assert response.status_code == 302

    def test_create_page_forbidden_for_student(self, client, db, student_user):
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

    def test_create_page_accessible_for_teacher(self, client, db, teacher_user):
        """Un enseignant peut accéder à la page de création."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get("/projects/create")
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_create_project_success(self, client, db, teacher_user):
        """Un enseignant peut créer un projet avec des données valides."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            "/projects/create",
            data={
                "title": "Nouveau Projet Test",
                "description": "Description complète du nouveau projet de test.",
                "domain": "informatique",
                "max_students": "2",
                "status": "open",
                "submit": "True",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        project = Project.query.filter_by(title="Nouveau Projet Test").first()
        assert project is not None
        assert project.teacher_id == teacher_user.id
        client.get("/auth/logout", follow_redirects=True)

    def test_create_project_missing_fields(self, client, db, teacher_user):
        """La création échoue si des champs obligatoires sont manquants."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            "/projects/create",
            data={
                "title": "",
                "description": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        project = Project.query.filter_by(title="").first()
        assert project is None
        client.get("/auth/logout", follow_redirects=True)


# ══════════════════════════════════════════════════════════════════════════
# TESTS MODIFICATION PROJET
# ══════════════════════════════════════════════════════════════════════════


class TestProjectEdit:
    """Tests de la route /projects/<id>/edit."""

    def test_edit_page_accessible_for_owner(self, client, db, teacher_user, sample_project):
        """L'enseignant propriétaire peut accéder à la page de modification."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get(f"/projects/{sample_project.id}/edit")
        assert response.status_code == 200
        client.get("/auth/logout", follow_redirects=True)

    def test_edit_forbidden_for_other_teacher(self, client, db, sample_project):
        """Un autre enseignant ne peut pas modifier le projet."""
        other = __import__("app.models.user", fromlist=["User"]).User(
            email="other@test.com",
            first_name="Autre",
            last_name="Prof",
            role="teacher",
            is_active=True,
        )
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

        client.post(
            "/auth/login",
            data={
                "email": "other@test.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.get(
            f"/projects/{sample_project.id}/edit",
            follow_redirects=False,
        )
        assert response.status_code in [302, 403]
        client.get("/auth/logout", follow_redirects=True)

    def test_edit_project_success(self, client, db, teacher_user, sample_project):
        """L'enseignant peut modifier son projet avec succès."""
        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            f"/projects/{sample_project.id}/edit",
            data={
                "title": "Projet Modifié",
                "description": "Nouvelle description du projet modifié.",
                "domain": "data",
                "max_students": "3",
                "status": "open",
                "submit": "True",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        updated = Project.query.get(sample_project.id)
        assert updated.title == "Projet Modifié"
        assert updated.domain == "data"
        client.get("/auth/logout", follow_redirects=True)


# ══════════════════════════════════════════════════════════════════════════
# TESTS SUPPRESSION PROJET
# ══════════════════════════════════════════════════════════════════════════


class TestProjectDelete:
    """Tests de la route POST /projects/<id>/delete."""

    def test_delete_forbidden_for_student(self, client, db, student_user, sample_project):
        """Un étudiant ne peut pas supprimer un projet."""
        client.post(
            "/auth/login",
            data={
                "email": student_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            f"/projects/{sample_project.id}/delete",
            follow_redirects=False,
        )
        assert response.status_code in [302, 403]
        assert Project.query.get(sample_project.id) is not None
        client.get("/auth/logout", follow_redirects=True)

    def test_delete_success_for_owner(self, client, db, teacher_user):
        """L'enseignant propriétaire peut supprimer son projet."""
        project = Project(
            title="Projet à Supprimer",
            description="Ce projet sera supprimé.",
            domain="informatique",
            max_students=1,
            status="open",
            teacher_id=teacher_user.id,
        )
        db.session.add(project)
        db.session.commit()
        project_id = project.id

        client.post(
            "/auth/login",
            data={
                "email": teacher_user.email,
                "password": "password123",
            },
            follow_redirects=True,
        )

        response = client.post(
            f"/projects/{project_id}/delete",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert Project.query.get(project_id) is None
        client.get("/auth/logout", follow_redirects=True)
        