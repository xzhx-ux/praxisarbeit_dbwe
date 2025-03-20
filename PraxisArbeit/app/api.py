# app/api.py
from flask import Blueprint, request, jsonify
from .models import User
from . import db

api_bp = Blueprint('api', __name__)

# Registierung des Benutzers mit api

@api_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Benutzername existiert bereits."}), 400
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registrierung erfolgreich."}), 201

# Anmeldung des Benutzers mit api

@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({"message": "Login erfolgreich.", "user_id": user.id}), 200
    else:
        return jsonify({"error": "Ungültige Anmeldedaten."}), 400
