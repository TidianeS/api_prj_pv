# run.py
from app import create_app
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le .env (FLASK_APP, FLASK_ENV)
load_dotenv()

# Crée une instance de l'application en utilisant notre factory
app = create_app()

if __name__ == '__main__':
    # Lance le serveur de développement intégré de Flask
    # Le host '0.0.0.0' le rend accessible depuis d'autres machines sur le réseau
    app.run(host='0.0.0.0', port=5000)