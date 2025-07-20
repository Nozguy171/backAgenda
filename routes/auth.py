from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..models import db, User, Role

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed = generate_password_hash(data['password'])
    user = User(
        username=data['username'],
        password=hashed,
        role=Role.COLABORADOR
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(msg='user created'), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify(msg='Bad credentials'), 401
    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token), 200
