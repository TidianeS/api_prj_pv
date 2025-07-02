# Fichier : app/auth.py

from functools import wraps
from flask import session, redirect, url_for, g

def login_required(f):
    """
    Décorateur simple et direct.
    Si l'utilisateur n'est pas dans la session, il est TOUJOURS
    redirigé vers la page de connexion.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifie si la clé 'user_id' existe dans la session
        if 'user_id' not in session:
            # Si non, redirige vers la page de connexion
            return redirect(url_for('main.login'))
        
        # Si oui, la fonction de la route originale est exécutée.
        return f(*args, **kwargs)
    return decorated_function

def load_logged_in_user():
    """
    Charge l'utilisateur depuis la session dans g.user avant chaque requête.
    Cela permet aux templates d'accéder à l'utilisateur via `g.user`.
    """
    user_id = session.get('user_id')
    g.user = user_id if user_id else None