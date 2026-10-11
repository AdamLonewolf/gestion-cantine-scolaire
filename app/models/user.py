from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """Modèle Utilisateur du système de cantine."""
    __tablename__ = 'users'

    ROLE_ADMIN = 'ADMIN'
    ROLE_GESTIONNAIRE = 'GESTIONNAIRE'
    ROLE_AGENT = 'AGENT_POINTAGE'
    ROLES = [ROLE_ADMIN, ROLE_GESTIONNAIRE, ROLE_AGENT]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(30), nullable=False, default=ROLE_GESTIONNAIRE)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        """Hache et stocke le mot de passe."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Vérifie le mot de passe avec le hash stocké."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_gestionnaire(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_GESTIONNAIRE]

    @property
    def is_agent(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_GESTIONNAIRE, self.ROLE_AGENT]

    def has_role(self, *roles):
        """Vérifie si l'utilisateur possède l'un des rôles spécifiés."""
        return self.role in roles

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
