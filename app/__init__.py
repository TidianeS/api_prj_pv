# Fichier : app/__init__.py

import os
from datetime import datetime, timezone
from flask import Flask
from flask_session import Session

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Configuration
    app.config.from_mapping(
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=False,
    )
    app.config.from_pyfile('config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialisation des extensions et modules
    Session(app)

    from . import db
    db.init_app(app)

    from . import auth
    app.before_request(auth.load_logged_in_user)
    
    # Enregistrement du blueprint principal
    from . import routes
    app.register_blueprint(routes.bp)

    # Injection de variables dans les templates
    @app.context_processor
    def inject_date_info():
        return {'now': datetime.now(timezone.utc)}
    
    return app