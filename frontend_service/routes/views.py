from flask import Blueprint, redirect
import os

views_bp = Blueprint('views', __name__)

@views_bp.route('/login')
def login():
    auth_url = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8000')
    return redirect(f"{auth_url}/login")  # Ya no es /auth/login 