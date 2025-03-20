# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO

db = SQLAlchemy()
mail = Mail()
socketio = SocketIO()

# Konfiguration per Umgebungsvariablen oder Fallbacks
MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() in ['true', '1', 't']
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = ['your-email@example.com']  # Passe das an

def create_app():
    # Templates und Static liegen im übergeordneten Ordner
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Grundkonfiguration – bitte anpassen!
    app.config['SECRET_KEY'] = 'SecretKeyPraxisArbeit'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://praxisarbeituser:praxisarbeitpassword@localhost/flask_app_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail-Konfiguration (SMTP-Daten anpassen!)
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@lab14.ifalabs.org'
    
    db.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    # Blueprints importieren und registrieren
    from .auth import auth_bp
    from .main import main_bp
    from .api import api_bp  # optional

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
