# Fichier : app/db.py

import psycopg2
from flask import current_app, g

def get_db():
    """
    Ouvre une nouvelle connexion à la base de données si aucune n'existe pour la requête actuelle.
    La connexion est stockée dans 'g', un objet spécial de Flask qui persiste pour la durée d'une seule requête.
    """
    if 'db' not in g:
        g.db = psycopg2.connect(current_app.config['DATABASE_URL'])
    return g.db

def close_db(e=None):
    """
    Ferme la connexion à la base de données si elle a été ouverte.
    Cette fonction sera automatiquement appelée par Flask à la fin de chaque requête.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """
    Fonction pour enregistrer les commandes de la base de données avec l'application Flask.
    """
    app.teardown_appcontext(close_db)