from flask import Blueprint, render_template

auth_view_bp = Blueprint('auth_view', __name__)

@auth_view_bp.route('/login')
def login():
    return render_template('login.html')

@auth_view_bp.route('/register')
def register():
    return render_template('register.html')
