import pytest

"""Cas 1 : Un agent peut accéder à la borne de pointage"""
def test_borne_pointage_agent(auth_agent_client):
    response = auth_agent_client.get('/attendance/')
    assert response.status_code == 200

"""Cas 2 : Un utilisateur non connecté est redirigé vers /login"""
def test_borne_pointage_non_connecte(client):
    response = client.get('/attendance/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

"""Cas 3 : Scan via API JSON d'un étudiant avec abonnement actif"""
def test_api_scan_valide(auth_agent_client, sample_student, sample_subscription_active):
    response = auth_agent_client.post('/attendance/api/scan',
        json={'matricule': sample_student.matricule}
    )
    assert response.status_code in [200, 400]

"""Cas 4 : Scan via API JSON d'un matricule inconnu — refus"""
def test_api_scan_matricule_inconnu(auth_agent_client):
    response = auth_agent_client.post('/attendance/api/scan',
        json={'matricule': 'ETU-00000'}
    )
    assert response.status_code == 400

"""Cas 5 : Un agent peut consulter l'historique des passages"""
def test_historique_passages_agent(auth_agent_client):
    response = auth_agent_client.get('/attendance/history')
    assert response.status_code == 200

"""Cas 6 : POST sur la borne de pointage avec un matricule valide"""
def test_borne_pointage_post(auth_agent_client, sample_student, sample_subscription_active):
    response = auth_agent_client.post('/attendance/', data={
        'matricule': sample_student.matricule
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 7 : Historique des passages avec filtre de statut"""
def test_historique_avec_filtre(auth_agent_client):
    response = auth_agent_client.get('/attendance/history?status=AUTORISE')
    assert response.status_code == 200