# Fichier : app/models.py (Version complète et corrigée)

from app.db import get_db
from psycopg2.extras import RealDictCursor

# ===============================================
# === MODÈLE POUR LES PROJETS
# ===============================================
class Project:
    """Modèle pour gérer les projets photovoltaïques."""

    @staticmethod
    def get_all():
        """Récupère tous les projets de la base de données."""
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id, parcelle_id, nom_projet, statut, puissance_kwc, TO_CHAR(date_creation, 'DD/MM/YYYY HH24:MI') as date_formatee "
            "FROM transition_energetique.projets_photovoltaiques ORDER BY date_creation DESC"
        )
        projects = cursor.fetchall()
        cursor.close()
        return projects

    @staticmethod
    def create(data):
        """
        Crée un nouveau projet dans la base de données.
        'data' est un dictionnaire (comme request.form) contenant les infos du projet.
        """
        db = get_db()
        cursor = db.cursor()
        sql = """
            INSERT INTO transition_energetique.projets_photovoltaiques (parcelle_id, nom_projet, statut, puissance_kwc, geom)
            VALUES (%s, %s, %s, %s, (SELECT ST_Centroid(geom) FROM cadastre.parcelles_06_2025 WHERE id = %s))
            RETURNING id;
        """
        try:
            cursor.execute(sql, (
                data.get('parcelle_id'),
                data.get('nom_projet'),
                data.get('statut'),
                data.get('puissance'),
                data.get('parcelle_id')
            ))
            new_id = cursor.fetchone()[0]
            db.commit()
            return new_id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def delete(project_id):
        """Supprime un projet par son ID."""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM transition_energetique.projets_photovoltaiques WHERE id = %s", (project_id,))
            deleted_rows = cursor.rowcount
            db.commit()
            return deleted_rows > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

# ===============================================
# === MODÈLE POUR LES PARCELLES (PARTIE MANQUANTE)
# ===============================================
class Parcel:
    @staticmethod
    def search(commune, section, numero):
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # On nettoie les entrées
        commune_clean = commune.strip()
        section_clean = section.strip().upper()
        
        # Le numéro DANS la BDD est TOUJOURS sur 4 chiffres (ex: 0134).
        # On doit donc toujours "padder" l'entrée de l'utilisateur pour la comparaison.
        numero_padded = numero.strip().zfill(4)
        
        # La requête utilise une structure fixe qui est la norme pour le cadastre.
        # C'est la version la plus robuste.
        sql = """
            SELECT id 
            FROM cadastre.parcelles_06_2025 
            WHERE 
                substring(id from 1 for 5) = %s
                AND substring(id from 9 for 2) = %s
                AND substring(id from 11 for 4) = %s
            LIMIT 10;
        """
        
        # Pour le débogage, vous pouvez décommenter la ligne suivante pour voir la requête finale.
        # print(cursor.mogrify(sql, (commune_clean, section_clean, numero_padded)).decode('utf-8'))
        
        cursor.execute(sql, (commune_clean, section_clean, numero_padded))
        
        parcels = cursor.fetchall()
        cursor.close()
        
        return parcels
