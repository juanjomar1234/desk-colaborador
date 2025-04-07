from flask import Blueprint, redirect, render_template, jsonify, request
from flask_jwt_extended import jwt_required
import os
import requests

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@views_bp.route('/login')
def login():
    """Página de login"""
    return render_template('login.html')

@views_bp.route('/check-auth')
def check_auth():
    """Endpoint para verificar autenticación"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'authenticated': False}), 401

    auth_url = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8000')
    try:
        response = requests.get(
            f"{auth_url}/verify",
            headers={'Authorization': token}
        )
        if response.status_code == 200:
            return jsonify({'authenticated': True}), 200
        return jsonify({'authenticated': False}), 401
    except:
        return jsonify({'authenticated': False}), 401 