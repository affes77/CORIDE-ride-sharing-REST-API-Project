from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_login import  LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from db import db

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400
    
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify({'message': 'username already taken'}), 400

    user = User.query.filter_by(email=email).first()
    if user is not None:
        return jsonify({'message': 'Email already taken'}), 400

    password_hash = generate_password_hash(password)
    user = User(username=username, email=email, password=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not check_password_hash(user.password, password) or user.email != email:
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username)

    response = jsonify({'access_token': access_token, 'expiration_time': 1800, 'username' : username})
    response.set_cookie('access_token', access_token, max_age=1800)
    return response, 200


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'logged_in_as': current_user}), 200


@auth_bp.route('/login_form', endpoint='login_form')
def login_route():
    return render_template('login.html')


@auth_bp.route('/register_form', endpoint='register_form')
def register_route():
    return render_template('register.html')


@auth_bp.route('/dashboard')
def dashboard():
    access_token = request.args.get('access_token')
    expiration_time = request.args.get('expiration_time')
    username = request.args.get('username')
    if not access_token or not expiration_time:
        return jsonify({'message': 'Missing required query parameters'}), 400
    
    return render_template('dashboard.html', access_token=access_token, expiration_time=expiration_time, username=username)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Delete the access token cookie
    response = jsonify({'message': 'Successfully logged out'})
    response.set_cookie('access_token', '', expires=0)
    return render_template('login.html')

