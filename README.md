# UniProjects — Plateforme de Gestion de Projets Étudiants

Plateforme web développée avec **Flask** permettant aux enseignants de soumettre
des sujets de projets et aux étudiants d'y postuler.

---

## Stack technique

- **Backend** : Python 3.x + Flask 3.0
- **Base de données** : SQLite (développement) via Flask-SQLAlchemy
- **Authentification** : Flask-Login + Werkzeug
- **Formulaires** : Flask-WTF + WTForms
- **Migrations** : Flask-Migrate (Alembic)
- **Frontend** : Jinja2 + Bootstrap 5 + CSS/JS personnalisés
- **Tests** : pytest + pytest-cov

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-repo/projet_univ.git
cd projet_univ
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créez un fichier `.env` à la racine :

```env
SECRET_KEY=votre-secret-key-tres-longue
DATABASE_URL=sqlite:///instance/projet_univ.db
FLASK_ENV=development
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre@email.com
MAIL_PASSWORD=votre-mot-de-passe
```

### 4. Initialiser la base de données

```bash
# Windows
set FLASK_APP=run.py
python -m flask db upgrade

# Linux/Mac
export FLASK_APP=run.py
flask db upgrade
```

### 5. Charger les données de test

```bash
python seed.py
```

### 6. Lancer le serveur

```bash
python run.py
```

L'application est accessible sur : **http://localhost:5000**

---

## Comptes de test

| Rôle | Email | Mot de passe |
|---|---|---|
| 👑 Administrateur | admin@univ.cm | password123 |
| 👨‍🏫 Enseignant | teacher@univ.fr | password123 |
| 👨‍🏫 Enseignant | prof.martin@univ.fr | password123 |
| 👨‍🎓 Étudiant | student@univ.fr | password123 |
| 👨‍🎓 Étudiant | etudiant2@univ.fr | password123 |
| 👨‍🎓 Étudiant | etudiant3@univ.fr | password123 |

---

## Structure du projet

```
projet_univ/
├── run.py                      # Point d'entrée
├── config.py                   # Configurations (Dev, Test, Prod)
├── seed.py                     # Données de test
├── requirements.txt            # Dépendances
├── .env                        # Variables d'environnement (non versionné)
├── .gitignore
├── README.md
├── instance/
│   └── projet_univ.db          # Base de données SQLite
├── migrations/                 # Migrations Flask-Migrate
├── app/
│   ├── __init__.py             # Factory create_app()
│   ├── extensions.py           # Extensions Flask
│   ├── models/
│   │   ├── user.py             # Modèle User
│   │   ├── project.py          # Modèle Project
│   │   └── application.py      # Modèle Application
│   ├── forms/
│   │   ├── auth.py             # LoginForm, RegisterForm
│   │   ├── project.py          # ProjectForm
│   │   └── application.py      # ApplicationForm
│   ├── routes/
│   │   ├── auth.py             # /auth/login /register /logout
│   │   ├── projects.py         # /projects/ CRUD
│   │   ├── applications.py     # /applications/
│   │   ├── dashboard.py        # /dashboard/
│   │   ├── admin.py            # /admin/
│   │   └── export.py           # /export/
│   ├── utils/
│   │   ├── decorators.py       # @role_required, @admin_required
│   │   ├── helpers.py          # paginate_query, get_stats
│   │   └── email.py            # Notifications email
│   ├── templates/              # Templates Jinja2
│   └── static/                 # CSS, JS, uploads
└── tests/
    ├── conftest.py             # Fixtures pytest
    ├── test_models.py          # Tests unitaires modèles
    ├── test_auth.py            # Tests authentification
    ├── test_projects.py        # Tests CRUD projets
    └── test_routes.py          # Tests intégration routes
```

---

## Endpoints principaux

| Méthode | URL | Description | Accès |
|---|---|---|---|
| GET | `/` | Page d'accueil | Public |
| GET | `/projects/` | Liste des projets | Public |
| GET | `/projects/<id>` | Détail projet | Public |
| GET/POST | `/auth/login` | Connexion | Public |
| GET/POST | `/auth/register` | Inscription | Public |
| GET | `/auth/logout` | Déconnexion | Connecté |
| GET | `/dashboard` | Dashboard (redirige selon rôle) | Connecté |
| GET/POST | `/projects/create` | Créer un projet | Enseignant |
| GET/POST | `/projects/<id>/edit` | Modifier un projet | Enseignant (propriétaire) |
| POST | `/projects/<id>/delete` | Supprimer un projet | Enseignant (propriétaire) |
| GET/POST | `/applications/apply/<id>` | Postuler | Étudiant |
| GET | `/applications/my` | Mes candidatures | Étudiant |
| GET | `/applications/project/<id>` | Candidatures reçues | Enseignant |
| POST | `/applications/<id>/accept` | Accepter candidature | Enseignant |
| POST | `/applications/<id>/reject` | Refuser candidature | Enseignant |
| GET | `/admin/users` | Gestion utilisateurs | Admin |
| GET | `/admin/stats` | Statistiques globales | Admin |
| GET | `/export/projects.csv` | Export projets CSV | Enseignant/Admin |
| GET | `/export/applications/<id>.csv` | Export candidatures CSV | Enseignant/Admin |

---

## Lancer les tests

```bash
# Tous les tests
pytest

# Avec détails
pytest -v

# Avec couverture de code
pytest --cov=app

# Un fichier spécifique
pytest tests/test_models.py -v
```

---

## Fonctionnalités

### Authentification & Rôles
- Inscription avec choix du rôle (étudiant / enseignant)
- Connexion sécurisée avec sessions Flask-Login
- Hash des mots de passe (Werkzeug)
- Protection CSRF (Flask-WTF)
- Middleware d'autorisation par rôle

### Gestion des Projets
- CRUD complet pour les enseignants
- Liste publique avec recherche et filtres
- Pagination (10 projets par page)
- Filtrage par domaine et statut

### Candidatures
- Postuler avec lettre de motivation et CV (PDF/DOC)
- Suivi des candidatures (en attente / acceptée / refusée)
- Accepter ou refuser les candidatures (enseignant)
- Notifications email simulées (log console)

### Dashboard
- Tableau de bord personnalisé selon le rôle
- Statistiques en temps réel
- Accès rapide aux actions principales

### Administration
- Gestion des comptes utilisateurs
- Activation / désactivation des comptes
- Statistiques globales de la plateforme
- Export CSV des projets et candidatures

---

## Sécurité

- Mots de passe hashés avec `werkzeug.security`
- Protection CSRF sur tous les formulaires
- Variables sensibles dans `.env` (non versionné)
- Validation côté serveur (WTForms)
- Contrôle d'accès par rôle sur toutes les routes sensibles
- Prévention des injections SQL via SQLAlchemy ORM

---

## Qualité du code

```bash
# Vérification PEP 8
flake8 .

# Formatage automatique
black .
```

---

*Projet réalisé dans le cadre de l'examen — Université de Douala*