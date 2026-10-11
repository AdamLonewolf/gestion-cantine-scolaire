from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.routes.decorators import role_required

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('/')
@login_required
@role_required(User.ROLE_ADMIN)
def list_users():
    """Liste des comptes utilisateurs ayant accès au système (réservé ADMIN)."""
    users = User.query.order_by(User.id.desc()).all()
    return render_template('users/list.html', users=users)

@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(User.ROLE_ADMIN)
def create_user():
    """Création d'un nouvel utilisateur par un administrateur connecté."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('users/create.html', roles=User.ROLES)

        try:
            new_user = AuthService.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                role=role
            )
            flash(f"Compte utilisateur '{new_user.username}' créé avec succès.", "success")
            return redirect(url_for('users.list_users'))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('users/create.html', roles=User.ROLES)

@user_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required(User.ROLE_ADMIN)
def toggle_user_status(user_id):
    """Activer / désactiver un compte utilisateur."""
    user = db.session.get(User, user_id)
    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for('users.list_users'))

    if user.id == current_user.id:
        flash("Vous ne pouvez pas désactiver votre propre compte administrateur.", "warning")
        return redirect(url_for('users.list_users'))

    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activé" if user.is_active else "désactivé"
    flash(f"Le compte de {user.full_name} a été {status_str}.", "info")
    return redirect(url_for('users.list_users'))
