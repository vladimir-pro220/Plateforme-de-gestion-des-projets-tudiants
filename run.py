"""
run.py
------
Point d'entrée de l'application Flask.
Lance le serveur de développement avec : python run.py
"""

import os
from app import create_app

# Sélection de la configuration selon FLASK_ENV
env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config["DEBUG"],
    )