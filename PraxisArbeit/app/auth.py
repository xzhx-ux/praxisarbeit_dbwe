# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User
from . import db, mail
from flask_mail import Message
import random, string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

# Registierung - Prüfung ob Benutzerv vorhanden wenn nicht erstellen
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        if User.query.filter_by(username=username).first():
            flash("Benutzername existiert bereits.")
            return redirect(url_for('auth.register'))
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registrierung erfolgreich. Bitte logge dich ein.")
        return redirect(url_for('auth.login'))
    return render_template('register.html')

# Login der Benutzer - Wenn die Daten ubereinstimmen weiterleiten an Dashboard
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.dashboard'))
        else:
            flash("Ungültige Anmeldedaten.")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# Ablauf password vergessen 
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user.set_password(new_password)
            db.session.commit()
            msg = Message("Dein neues Passwort", recipients=[email])
            msg.body = f"Hallo {user.username},\n\nDein neues Passwort lautet: {new_password}\nBitte ändere es nach dem Login."
            mail.send(msg)
            flash("Ein neues Passwort wurde an deine Email gesendet.")
        else:
            flash("Keine Registrierung mit dieser Email gefunden.")
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')
