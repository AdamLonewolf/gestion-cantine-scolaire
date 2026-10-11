import re
from app import db
from app.models.user import User

class AuthService:
    """Service gérant l'authentification, les politiques de sécurité et les utilisateurs."""

    @staticmethod
    def validate_password_policy(password):
        """
        RG-USR-04 : Le mot de passe doit comporter au minimum 8 caractères
        et contenir au moins une lettre et un chiffre.
        """
        if not password:
            return False, "Le mot de passe ne peut pas être vide."
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères."
        if not re.search(r'[A-Za-z]', password):
            return False, "Le mot de passe doit contenir au moins une lettre."
        if not re.search(r'\d', password):
            return False, "Le mot de passe doit contenir au moins un chiffre."
        return True, ""

    @staticmethod
    def validate_username(username):
        """Valide le format du nom d'utilisateur (alphanumérique + _ - , 3 à 30 caractères)."""
        if not username or not (3 <= len(username) <= 30):
            return False, "Le nom d'utilisateur doit comporter entre 3 et 30 caractères."
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores."
        return True, ""

    @staticmethod
    def create_user(username, email, password, full_name, role=User.ROLE_GESTIONNAIRE, is_active=True):
        """
        Crée un nouvel utilisateur en respectant les règles d'intégrité et de sécurité.
        RG-USR-02, RG-USR-03, RG-USR-04, RG-USR-05.
        """
        # Nettoyage
        username = (username or "").strip()
        email = (email or "").strip().lower()
        full_name = (full_name or "").strip()

        # Validation username
        u_valid, u_err = AuthService.validate_username(username)
        if not u_valid:
            raise ValueError(u_err)

        # Validation email
        if not email or '@' not in email:
            raise ValueError("L'adresse email est invalide.")

        # Validation rôle
        if role not in User.ROLES:
            raise ValueError(f"Rôle invalide. Rôles autorisés: {', '.join(User.ROLES)}")

        # Validation mot de passe
        p_valid, p_err = AuthService.validate_password_policy(password)
        if not p_valid:
            raise ValueError(p_err)

        # Unicité username
        if User.query.filter_by(username=username).first():
            raise ValueError(f"Le nom d'utilisateur '{username}' est déjà utilisé.")

        # Unicité email
        if User.query.filter_by(email=email).first():
            raise ValueError(f"L'adresse email '{email}' est déjà associée à un compte.")

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            is_active=is_active
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def authenticate(username_or_email, password):
        """
        Authentifie un utilisateur avec vérification de son statut actif.
        RG-USR-06 : Un compte inactif ne peut pas se connecter.
        """
        identifier = (username_or_email or "").strip()
        if not identifier or not password:
            return None, "Identifiant et mot de passe requis."

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user:
            return None, "Identifiant ou mot de passe incorrect."

        if not user.check_password(password):
            return None, "Identifiant ou mot de passe incorrect."

        if not user.is_active:
            return None, "Ce compte est désactivé. Veuillez contacter l'administrateur."

        return user, ""
