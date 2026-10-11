from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion au système (pas d'inscription directe)."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        user, error_msg = AuthService.authenticate(username, password)
        if user:
            login_user(user, remember=remember)
            flash(f"Ravi de vous revoir, {user.full_name} !", "success")
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash(error_msg, "danger")

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion de l'utilisateur."""
    logout_user()
    flash("Vous avez été déconnecté avec succès.", "info")
    return redirect(url_for('auth.login'))
