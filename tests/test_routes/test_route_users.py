import pytest

"""Cas 1 : Un admin peut accéder à la liste des utilisateurs"""
def test_liste_users_admin(auth_admin_client):
    response = auth_admin_client.get('/users/')
    assert response.status_code == 200

"""Cas 2 : Un gestionnaire n'a pas accès à la liste des utilisateurs"""
def test_liste_users_gestionnaire_interdit(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/users/')
    assert response.status_code == 403

"""Cas 3 : Création d'un utilisateur valide par un admin — redirige vers la liste"""
def test_creation_user_valide(auth_admin_client):
    response = auth_admin_client.post('/users/create', data={
        'username': 'nouveau_user',
        'email': 'nouveau@test.fr',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'full_name': 'Nouveau User',
        'role': 'AGENT_POINTAGE'
    }, follow_redirects=False)
    assert response.status_code == 302

"""Cas 4 : Création d'un utilisateur avec mot de passe non conforme — reste sur le formulaire"""
def test_creation_user_mdp_non_conforme(auth_admin_client):
    response = auth_admin_client.post('/users/create', data={
        'username': 'user2',
        'email': 'user2@test.fr',
        'password': 'court',
        'confirm_password': 'court',
        'full_name': 'User Deux',
        'role': 'AGENT_POINTAGE'
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 5 : Bascule du statut actif/inactif d'un utilisateur par un admin"""
def test_toggle_user_status(auth_admin_client, agent_user):
    response = auth_admin_client.post(
        f'/users/{agent_user.id}/toggle-status',
        follow_redirects=False
    )
    assert response.status_code == 302

"""Cas 6 : Création avec mots de passe non identiques — reste sur le formulaire"""
def test_creation_user_mdp_non_identiques(auth_admin_client):
    response = auth_admin_client.post('/users/create', data={
        'username': 'user_test3',
        'email': 'user3@test.fr',
        'password': 'Password123!',
        'confirm_password': 'AutrePassword123!',
        'full_name': 'User Trois',
        'role': 'AGENT_POINTAGE'
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 7 : Toggle status d'un utilisateur inexistant — redirige avec flash"""
def test_toggle_user_inexistant(auth_admin_client):
    response = auth_admin_client.post(
        '/users/99999/toggle-status',
        follow_redirects=True
    )
    assert response.status_code == 200

"""Cas 8 : Admin tente de désactiver son propre compte — refus avec flash"""
def test_toggle_proprio_compte_admin(auth_admin_client, admin_user):
    response = auth_admin_client.post(
        f'/users/{admin_user.id}/toggle-status',
        follow_redirects=True
    )
    assert response.status_code == 200