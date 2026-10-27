import pytest
from flask import url_for

# Tests sur la connexion à la plateforme

"""
    CAS 1 : Les données du User sont correctes et il accède à la plateforme
"""
def test_connexion_valide (client, admin_user, app):
    #Préparation des identifiants
    identifiants = {
        "username" : admin_user.username,
        "password" : "Password123!"
    }
    #Envoi de la requête de connexion
    response = client.post("/login", data = identifiants)
    #Vérification du résultat
    assert response.status_code == 302
    
    with app.test_request_context():
        expected_url = url_for('main.dashboard')

    assert expected_url in response.location #Vérifie si l'url recherchée se trouve bien dans response.location


"""
    CAS 2: Vérifie qu'un utilisateur non authentifié est immédiatement 
    redirigé vers la page de connexion.
"""
def test_tentative_acces_anonyme(client, app):
  
  with app.test_request_context():
        protected_url = url_for('main.dashboard')
        login_url = url_for("auth.login") 
  response = client.get(protected_url, follow_redirects=False)
  assert response.status_code == 302
  assert login_url in response.location


"""
    CAS 3: Vérifie qu'un utilisateur avec un compte désactivé ne peut pas se connecter.
"""
def test_login_compte_desactive(client, agent_user_desactive):

    identifiants = {
            "username" : agent_user_desactive.username,
            "password" : "Password123!"
        }

    response = client.post('/login', data=identifiants)
    assert response.status_code == 200

"""Cas 4 : Un utilisateur déjà connecté qui accède à /login est redirigé vers le dashboard"""
def test_login_deja_connecte(auth_admin_client):
    response = auth_admin_client.get('/login', follow_redirects=False)
    assert response.status_code == 302
    assert 'dashboard' in response.location or '/' in response.location

"""Cas 5 : Déconnexion d'un utilisateur connecté"""
def test_logout(auth_admin_client):
    response = auth_admin_client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert 'login' in response.location



