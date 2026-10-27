import pytest
from app.services.auth_service import AuthService
from app.models.user import User

"""Cas 1 : Mot de passe vide — lève une ValueError"""
def test_create_user_password_vide(app):
    with pytest.raises(ValueError):
        AuthService.create_user(
            username="user_test",
            email="user@test.fr",
            password="",
            full_name="User Test",
            role=User.ROLE_AGENT
        )

"""Cas 2 : Username trop court (< 3 caractères) — lève une ValueError"""
def test_create_user_username_trop_court(app):
    with pytest.raises(ValueError):
        AuthService.create_user(
            username="ab",
            email="user@test.fr",
            password="Password123!",
            full_name="User Test",
            role=User.ROLE_AGENT
        )

"""Cas 3 : Username avec caractères invalides — lève une ValueError"""
def test_create_user_username_caracteres_invalides(app):
    with pytest.raises(ValueError):
        AuthService.create_user(
            username="user@invalide!",
            email="user@test.fr",
            password="Password123!",
            full_name="User Test",
            role=User.ROLE_AGENT
        )

"""Cas 4 : Email invalide — lève une ValueError"""
def test_create_user_email_invalide(app):
    with pytest.raises(ValueError):
        AuthService.create_user(
            username="user_test",
            email="pasunemail",
            password="Password123!",
            full_name="User Test",
            role=User.ROLE_AGENT
        )

"""Cas 5 : Rôle invalide — lève une ValueError"""
def test_create_user_role_invalide(app):
    with pytest.raises(ValueError):
        AuthService.create_user(
            username="user_test",
            email="user@test.fr",
            password="Password123!",
            full_name="User Test",
            role="SUPER_ADMIN"
        )

"""Cas 6 : Username en doublon — lève une ValueError"""
def test_create_user_username_doublon(app, admin_user):
    with pytest.raises(ValueError):
        AuthService.create_user(
            username="admin_test",
            email="autre@test.fr",
            password="Password123!",
            full_name="Autre Admin",
            role=User.ROLE_ADMIN
        )

"""Cas 7 : Email en doublon — lève une ValueError"""
def test_create_user_email_doublon(app, admin_user):
    with pytest.raises(ValueError):
        AuthService.create_user(
            username="autre_admin",
            email="admin_test@test.fr",
            password="Password123!",
            full_name="Autre Admin",
            role=User.ROLE_ADMIN
        )

"""Cas 8 : Authentification avec identifiant et mot de passe vides"""
def test_authenticate_champs_vides(app):
    user, msg = AuthService.authenticate("", "")
    assert user is None
    assert msg is not None

"""Cas 9 : Authentification avec un username inexistant"""
def test_authenticate_user_inexistant(app):
    user, msg = AuthService.authenticate("inconnu", "Password123!")
    assert user is None

"""Cas 10 : Authentification avec un mauvais mot de passe"""
def test_authenticate_mauvais_password(app, admin_user):
    user, msg = AuthService.authenticate("admin_test", "mauvais")
    assert user is None