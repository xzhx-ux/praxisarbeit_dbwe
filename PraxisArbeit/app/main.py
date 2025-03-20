# app/main.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User, Friend, Chat
from . import db, socketio
from flask_socketio import emit, join_room, leave_room
import datetime

main_bp = Blueprint('main', __name__)

# Website Anwendungen und Funktionen der Webseite - Freunde hinzufügen

@main_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    friends_query = Friend.query.filter_by(user_id=user.id).all()
    # Hole die Freund-Objekte (hier nehmen wir an, dass Friend.friend_id auf den Freund zeigt)
    friend_users = [User.query.get(friend.friend_id) for friend in friends_query]
    search_query = request.args.get('q', '')
    search_results = []
    if search_query:
        if len(search_query) == 1:
            search_results = User.query.filter(User.username.like(f'{search_query}%')).all()
        else:
            search_results = User.query.filter(User.username.like(f'%{search_query}%')).all()
        search_results = [u for u in search_results if u.id != user.id]
    return render_template('dashboard.html', user=user, friends=friend_users,
                           search_results=search_results, search_query=search_query)

# Überprüfung, ob der Benutzer bereit als Freunde in der Liste ist

@main_bp.route('/add_friend/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    if Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first():
        flash("Dieser Benutzer ist bereits in deiner Freundesliste.")
        return redirect(url_for('main.dashboard'))
    new_friend = Friend(user_id=user_id, friend_id=friend_id)
    db.session.add(new_friend)
    db.session.commit()
    flash("Freund hinzugefügt.")
    return redirect(url_for('main.dashboard'))

# Freund entfernen

@main_bp.route('/remove_friend/<int:friend_id>', methods=['POST'])
def remove_friend(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    friendship = Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash("Freund entfernt.")
    return redirect(url_for('main.dashboard'))

# Chat

@main_bp.route('/chat/<int:friend_id>', methods=['GET'])
def chat(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    current_user_id = session['user_id']
    friend_user = User.query.get(friend_id)
    chats = Chat.query.filter(
        ((Chat.sender_id == current_user_id) & (Chat.receiver_id == friend_id)) |
        ((Chat.sender_id == friend_id) & (Chat.receiver_id == current_user_id))
    ).order_by(Chat.timestamp.asc()).all()
    return render_template('chat.html', friend=friend_user, current_user_id=current_user_id, chats=chats)

# Profilebearbeitung

@main_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        if 'delete' in request.form:
            db.session.delete(user)
            db.session.commit()
            session.clear()
            flash("Profil gelöscht.")
            return redirect(url_for('auth.register'))
        else:
            user.username = request.form.get('username')
            user.name = request.form.get('name')
            user.email = request.form.get('email')
            new_password = request.form.get('password')
            if new_password:
                user.set_password(new_password)
            user.profile_pic = request.form.get('profile_pic')
            db.session.commit()
            flash("Profil aktualisiert.")
            return redirect(url_for('main.dashboard'))
    return render_template('profile.html', user=user)

# SocketIO Events für den Echtzeit-Chat
@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f"{data['username']} ist beigetreten."}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    room = data['room']
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    new_chat = Chat(sender_id=data['sender_id'], receiver_id=data['receiver_id'], message=data['message'])
    db.session.add(new_chat)
    db.session.commit()
    emit('receive_message', {
        'username': data['username'],
        'message': data['message'],
        'timestamp': timestamp
    }, room=room)
