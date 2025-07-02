# Fichier : app/routes.py (Version MODIFIÉE et simplifiée de votre code)

from flask import (
    Blueprint, request, jsonify, session, render_template, redirect, url_for, current_app
)
# On importe les modèles que nous venons de créer
from app.models import Project, Parcel
from app.auth import login_required
import psycopg2

# On garde un seul Blueprint comme dans votre version originale.
bp = Blueprint('main', __name__)

# ===============================================
# === Routes pour les Pages HTML (INCHANGÉES)
# ===============================================

@bp.route('/')
@login_required
def index():
    return render_template('index.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    # CETTE FONCTION RESTE EXACTEMENT LA MÊME QUE DANS VOTRE FICHIER.
    # ELLE N'INTERAGIT PAS AVEC LES MODÈLES PROJECT OU PARCEL.
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_config_url = current_app.config['DATABASE_URL']
        db_parts = psycopg2.extensions.parse_dsn(db_config_url)
        conn_string_test = f"postgresql://{username}:{password}@{db_parts['host']}:{db_parts['port']}/{db_parts['dbname']}"
        error = None
        try:
            conn_test = psycopg2.connect(conn_string_test)
            conn_test.close()
        except psycopg2.OperationalError:
            error = "Identifiants invalides."
        if error is None:
            session.clear()
            session['user_id'] = username
            return redirect(url_for('main.index'))
        return render_template('login.html', error=error)
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

# ===============================================
# === Routes pour l'API (SIMPLIFIÉES GRÂCE AUX MODÈLES)
# ===============================================

@bp.route('/api/projects', methods=('GET',))
@login_required
def get_projects():
    """[API] Retourne la liste des projets en appelant le modèle."""
    try:
        projects = Project.get_all()
        return jsonify(projects)
    except Exception as e:
        return jsonify({'error': f"Erreur serveur: {e}"}), 500


@bp.route('/api/projects', methods=('POST',))
@login_required
def add_project():
    """[API] Ajoute un nouveau projet en appelant le modèle."""
    if not request.form.get('parcelle_id') or not request.form.get('nom_projet'):
        return jsonify({'error': 'ID Parcelle et Nom du projet sont requis'}), 400
    
    try:
        new_id = Project.create(request.form)
        return jsonify({'success': True, 'id': new_id}), 201
    except Exception as e:
        return jsonify({'error': f"Erreur base de données: {e}"}), 500


@bp.route('/api/projects/<int:project_id>', methods=('DELETE',))
@login_required
def delete_project(project_id):
    """[API] Supprime un projet en appelant le modèle."""
    try:
        if Project.delete(project_id):
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Projet non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': f"Erreur base de données: {e}"}), 500


@bp.route('/api/parcels/search')
@login_required
def search_parcels():
    """[API] Recherche des parcelles en appelant le modèle."""
    commune = request.args.get('commune')
    section = request.args.get('section')
    numero = request.args.get('numero')

    if not all([commune, section, numero]):
        return jsonify({'error': 'Paramètres de recherche manquants'}), 400
    
    try:
        parcels = Parcel.search(commune, section, numero)
        return jsonify(parcels)
    except Exception as e:
        return jsonify({'error': f"Erreur base de données: {e}"}), 500