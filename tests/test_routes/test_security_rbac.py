import pytest
from flask import url_for



#Tests sur le Contrôle d'Accès basé sur les Rôles (RBAC)

"""
    CAS 1 : vérifier qu'un admin connecté accède bien au Dashboard sans être redirigé
"""
def test_acces_dashboard_autorise(auth_admin_client, app):

    with app.test_request_context():
        dashboard_url = url_for("main.dashboard")
    response = auth_admin_client.get(dashboard_url)
    assert response.status_code == 200


"""
    CAS 2 : Un utilisateur connecté avec le rôle AGENT ne doit pas 
    pouvoir accéder à la liste des utilisateurs (réservée à l'ADMIN)
"""
def test_agent_interdit_acces_gestion_utilisateurs(auth_agent_client, app) : 

    with app.test_request_context():
        url_protected = url_for('users.list_users')
    response = auth_agent_client.get(url_protected)
    assert response.status_code == 403 # Retourne un 403 Forbidden


"""
    CAS 3 : Vérifie qu'un GESTIONNAIRE reçoit aussi un 403 sur cette route admin.
"""
def test_gestionnaire_interdit_acces_gestion_utilisateurs(auth_gestionnaire_client, app):
   
    with app.test_request_context():
        url_protegee = url_for('users.list_users')
        
    response = auth_gestionnaire_client.get(url_protegee)
    assert response.status_code == 403


"""
    CAS 4 : Vérifie que l'ADMIN (le rôle légitime) accède bien à la page (200 OK).
"""
def test_admin_autorise_acces_gestion_utilisateurs(auth_admin_client, app):
    with app.test_request_context():
        url_protegee = url_for('users.list_users')
        
    response = auth_admin_client.get(url_protegee)
    assert response.status_code == 200

"""Cas 5 : Accès direct à une route protégée sans session — retourne 401 ou 302"""
def test_acces_sans_session_retourne_401_ou_302(client):
    response = client.get('/students/', follow_redirects=False)
    assert response.status_code in [302, 401]

"""Cas 6 : Accès à une URL inexistante retourne 404"""
# def test_page_404(auth_admin_client):
#     response = auth_admin_client.get('/route/qui/nexiste/pas')
#     assert response.status_code == 404

"""Cas 7 : load_user est appelé lors de chaque requête authentifiée"""
def test_load_user_appele(auth_admin_client):
    response = auth_admin_client.get('/')
    assert response.status_code == 200