import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"

def create_app(config_name='default'):
    """Application Factory Flask."""
    from config import config

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Chargement de l'utilisateur pour Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Enregistrement des Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.main_routes import main_bp
    from app.routes.student_routes import student_bp
    from app.routes.subscription_routes import subscription_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.attendance_routes import attendance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(attendance_bp)

    # Enregistrement des commandes CLI
    from app.cli import register_commands
    register_commands(app)

    # Gestionnaires d'erreurs HTTP personnalisés
    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
