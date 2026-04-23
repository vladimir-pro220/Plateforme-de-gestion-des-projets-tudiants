"""
seed.py
-------
Script de seed : crée les comptes de test et les données de démonstration.
Usage : python seed.py
"""

import os
import sys

# Ajoute la racine du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.project import Project
from app.models.application import Application


def seed_users(db):
    """Crée les comptes de test : admin, teacher, student."""

    print("  → Création des utilisateurs...")

    # Admin
    admin = User(
        email="admin@univ.cm",
        first_name="Super",
        last_name="Admin",
        role="admin",
        is_active=True,
    )
    admin.set_password("password123")

    # Enseignants
    teacher1 = User(
        email="teacher@univ.fr",
        first_name="Jean",
        last_name="Dupont",
        role="teacher",
        is_active=True,
    )
    teacher1.set_password("password123")

    teacher2 = User(
        email="prof.martin@univ.fr",
        first_name="Marie",
        last_name="Martin",
        role="teacher",
        is_active=True,
    )
    teacher2.set_password("password123")

    # Étudiants
    student1 = User(
        email="student@univ.fr",
        first_name="Alice",
        last_name="Durand",
        role="student",
        is_active=True,
    )
    student1.set_password("password123")

    student2 = User(
        email="etudiant2@univ.fr",
        first_name="Bob",
        last_name="Nguyen",
        role="student",
        is_active=True,
    )
    student2.set_password("password123")

    student3 = User(
        email="etudiant3@univ.fr",
        first_name="Claire",
        last_name="Mballa",
        role="student",
        is_active=True,
    )
    student3.set_password("password123")

    users = [admin, teacher1, teacher2, student1, student2, student3]
    db.session.add_all(users)
    db.session.flush()  # Pour obtenir les IDs avant commit

    print(f"     ✓ {len(users)} utilisateurs créés.")
    return teacher1, teacher2, student1, student2, student3


def seed_projects(db, teacher1, teacher2):
    """Crée les projets de test."""

    print("  → Création des projets...")

    projects = [
        Project(
            title="Système de détection d'anomalies par Machine Learning",
            description=(
                "Ce projet vise à développer un système intelligent capable de "
                "détecter des anomalies dans des flux de données en temps réel. "
                "L'étudiant devra maîtriser les algorithmes de clustering (K-means, "
                "DBSCAN) et les réseaux de neurones (Autoencoder). "
                "Compétences requises : Python, scikit-learn, TensorFlow."
            ),
            domain="Intelligence Artificielle",
            max_students=2,
            status="open",
            teacher_id=teacher1.id,
        ),
        Project(
            title="Application mobile de gestion de budget personnel",
            description=(
                "Développement d'une application cross-platform (React Native) "
                "permettant de gérer ses dépenses, revenus et objectifs d'épargne. "
                "Intégration d'une API bancaire simulée et génération de rapports PDF. "
                "Compétences requises : JavaScript, React Native, Node.js."
            ),
            domain="Développement Mobile",
            max_students=1,
            status="open",
            teacher_id=teacher1.id,
        ),
        Project(
            title="Plateforme de e-learning avec suivi adaptatif",
            description=(
                "Conception d'une plateforme d'apprentissage en ligne intégrant "
                "un moteur de recommandation basé sur les performances de l'étudiant. "
                "Le système adapte le contenu selon le niveau et les lacunes détectées. "
                "Compétences requises : Python, Django, PostgreSQL, algorithmes de recommandation."
            ),
            domain="Éducation Numérique",
            max_students=3,
            status="open",
            teacher_id=teacher2.id,
        ),
        Project(
            title="Analyse de sentiment des réseaux sociaux",
            description=(
                "Collecte et analyse de tweets en temps réel via l'API Twitter. "
                "Classification des sentiments (positif, négatif, neutre) avec "
                "des modèles NLP (BERT, transformers). Dashboard de visualisation. "
                "Compétences requises : Python, NLP, API REST, Data Visualization."
            ),
            domain="Data Science",
            max_students=2,
            status="open",
            teacher_id=teacher2.id,
        ),
        Project(
            title="Système de gestion de stock avec IoT",
            description=(
                "Développement d'un système de gestion de stock connecté "
                "utilisant des capteurs IoT (Raspberry Pi) pour le suivi "
                "en temps réel des inventaires. Alertes automatiques et "
                "tableau de bord web. "
                "Compétences requises : Python, Flask, MQTT, bases de données."
            ),
            domain="Internet des Objets",
            max_students=2,
            status="open",
            teacher_id=teacher1.id,
        ),
        Project(
            title="Blockchain pour la certification des diplômes",
            description=(
                "Implémentation d'une solution blockchain (Ethereum) pour "
                "la vérification et certification des diplômes universitaires. "
                "Smart contracts en Solidity et interface web3. "
                "Compétences requises : Blockchain, Solidity, Web3.js, Python."
            ),
            domain="Blockchain",
            max_students=1,
            status="closed",
            teacher_id=teacher2.id,
        ),
    ]

    db.session.add_all(projects)
    db.session.flush()

    print(f"     ✓ {len(projects)} projets créés.")
    return projects


def seed_applications(db, projects, student1, student2, student3):
    """Crée les candidatures de test."""

    print("  → Création des candidatures...")

    applications = [
        # Alice postule au projet IA
        Application(
            student_id=student1.id,
            project_id=projects[0].id,
            motivation=(
                "Je suis passionnée par l'intelligence artificielle et j'ai déjà "
                "réalisé plusieurs projets de machine learning durant ma licence. "
                "J'ai une bonne maîtrise de Python, scikit-learn et TensorFlow. "
                "Ce projet correspond parfaitement à mon orientation professionnelle "
                "vers la data science et je suis très motivée pour contribuer."
            ),
            status="accepted",
        ),
        # Alice postule aussi au projet Data Science
        Application(
            student_id=student1.id,
            project_id=projects[3].id,
            motivation=(
                "L'analyse de sentiment est un domaine qui m'intéresse beaucoup. "
                "J'ai déjà travaillé avec des APIs REST et j'aimerais approfondir "
                "mes connaissances en NLP avec des modèles comme BERT."
            ),
            status="pending",
        ),
        # Bob postule au projet Mobile
        Application(
            student_id=student2.id,
            project_id=projects[1].id,
            motivation=(
                "Développeur mobile autodidacte, j'ai publié deux applications "
                "sur le Play Store. Je maîtrise React Native et Node.js. "
                "Ce projet me permettrait de professionnaliser mes compétences "
                "et d'acquérir une expérience en contexte académique."
            ),
            status="pending",
        ),
        # Bob postule au projet IA
        Application(
            student_id=student2.id,
            project_id=projects[0].id,
            motivation=(
                "Très intéressé par le machine learning, j'ai suivi plusieurs "
                "MOOCs sur Coursera (Andrew Ng). Je souhaite appliquer ces "
                "connaissances sur un projet concret et structuré."
            ),
            status="rejected",
        ),
        # Claire postule au projet e-learning
        Application(
            student_id=student3.id,
            project_id=projects[2].id,
            motivation=(
                "Étudiante en master informatique spécialisation éducation numérique, "
                "ce projet s'inscrit directement dans mon domaine de recherche. "
                "J'ai déjà développé un prototype de système de recommandation "
                "dans le cadre de mon stage de licence."
            ),
            status="pending",
        ),
        # Claire postule au projet IoT
        Application(
            student_id=student3.id,
            project_id=projects[4].id,
            motivation=(
                "Passionnée par l'IoT, j'ai réalisé plusieurs projets avec "
                "Arduino et Raspberry Pi. Je maîtrise Python et les protocoles "
                "de communication MQTT et HTTP. Ce projet est une excellente "
                "opportunité de mettre en pratique mes compétences."
            ),
            status="pending",
        ),
    ]

    db.session.add_all(applications)
    print(f"     ✓ {len(applications)} candidatures créées.")


def run_seed():
    """Fonction principale du seed."""
    app = create_app("development")

    with app.app_context():
        print("\n========================================")
        print("  UniProjects — Script de seed")
        print("========================================\n")

        # Vérifie si des données existent déjà
        if User.query.count() > 0:
            print("⚠️  Des données existent déjà en base.")
            response = input("   Voulez-vous réinitialiser ? (o/N) : ").strip().lower()
            if response != "o":
                print("❌ Seed annulé.")
                return

            print("  → Suppression des données existantes...")
            Application.query.delete()
            Project.query.delete()
            User.query.delete()
            db.session.commit()
            print("     ✓ Base de données vidée.\n")

        try:
            # Création des données
            teacher1, teacher2, student1, student2, student3 = seed_users(db)
            projects = seed_projects(db, teacher1, teacher2)
            seed_applications(db, projects, student1, student2, student3)

            db.session.commit()

            print("\n✅ Seed terminé avec succès !\n")
            print("─" * 40)
            print("  COMPTES DE TEST")
            print("─" * 40)
            print("  👤 Admin    : admin@univ.cm / password123")
            print("  👨‍🏫 Enseignant: teacher@univ.fr / password123")
            print("  👨‍🏫 Enseignant: prof.martin@univ.fr / password123")
            print("  👨‍🎓 Étudiant  : student@univ.fr / password123")
            print("  👨‍🎓 Étudiant  : etudiant2@univ.fr / password123")
            print("  👨‍🎓 Étudiant  : etudiant3@univ.fr / password123")
            print("─" * 40)
            print(f"  📁 {len(projects)} projets créés")
            print("  📨 6 candidatures créées")
            print("─" * 40)
            print("\n🚀 Lance le serveur avec : python run.py\n")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur durant le seed : {e}")
            raise


if __name__ == "__main__":
    run_seed()