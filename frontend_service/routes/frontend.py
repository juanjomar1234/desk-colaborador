from flask import Blueprint, render_template, jsonify, request, current_app
import requests

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    return render_template('index.html')

@frontend_bp.route('/login')
def login():
    return render_template('login.html')

@frontend_bp.route('/check-auth', methods=['GET'])
def check_auth():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'authenticated': False}), 401
    
    # Verificar token con auth-service
    auth_url = f"{current_app.config['AUTH_SERVICE_URL']}/api/auth/check-auth"
    try:
        response = requests.get(
            auth_url,
            headers={'Authorization': token}
        )
        if response.status_code == 200:
            return jsonify({'authenticated': True}), 200
    except:
        pass
    
    return jsonify({'authenticated': False}), 401
