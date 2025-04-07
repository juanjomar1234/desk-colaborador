import os
from flask import redirect

@views_bp.route('/login')
def login():
    auth_url = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8000')
    return redirect(f"{auth_url}/login")  # Ya no es /auth/login 