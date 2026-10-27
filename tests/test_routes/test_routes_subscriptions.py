import pytest
from unittest.mock import patch

"""Cas 1 : Un gestionnaire peut accéder à la liste des abonnements"""
def test_liste_abonnements_gestionnaire(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/subscriptions/')
    assert response.status_code == 200

"""Cas 2 : Un agent n'a pas accès à la liste des abonnements"""
def test_liste_abonnements_agent_interdit(auth_agent_client):
    response = auth_agent_client.get('/subscriptions/')
    assert response.status_code == 403

"""Cas 3 : Un gestionnaire peut accéder au formulaire de nouvel abonnement"""
def test_formulaire_nouvel_abonnement(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/subscriptions/new')
    assert response.status_code == 200

"""Cas 4 : Création d'un abonnement valide — redirige vers la fiche étudiant"""
def test_creation_abonnement_valide(auth_gestionnaire_client, sample_student, sample_plan):
    response = auth_gestionnaire_client.post('/subscriptions/new', data={
        'student_id': sample_student.id,
        'plan_id': sample_plan.id,
        'start_date': '2026-10-01',
        'end_date': '2026-10-31',
        'auto_renew': 'on'
    }, follow_redirects=False)
    assert response.status_code == 302

"""Cas 5 : Renouvellement d'un abonnement expiré — redirige vers la fiche étudiant"""
def test_renouvellement_abonnement(auth_gestionnaire_client, sample_subscription_expire):
    response = auth_gestionnaire_client.post(
        f'/subscriptions/{sample_subscription_expire.id}/renew',
        follow_redirects=False
    )
    assert response.status_code == 302

"""Cas 6 : Résiliation d'un abonnement actif — redirige vers la fiche étudiant"""
def test_resiliation_abonnement(auth_gestionnaire_client, sample_subscription_active):
    response = auth_gestionnaire_client.post(
        f'/subscriptions/{sample_subscription_active.id}/cancel',
        follow_redirects=False
    )
    assert response.status_code == 302

"""Cas 7 : Création d'abonnement avec données invalides — reste sur formulaire"""
def test_creation_abonnement_invalide(auth_gestionnaire_client, sample_student, sample_plan):
    response = auth_gestionnaire_client.post('/subscriptions/new', data={
        'student_id': sample_student.id,
        'plan_id': sample_plan.id,
        'start_date': '2026-10-31',
        'end_date': '2026-10-01',  # end < start
        'auto_renew': 'on'
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 8 : Renouvellement d'un abonnement inexistant — redirige avec flash"""
def test_renouvellement_abonnement_inexistant(auth_gestionnaire_client):
    response = auth_gestionnaire_client.post(
        '/subscriptions/99999/renew',
        follow_redirects=True
    )
    assert response.status_code == 200

"""Cas 9 : Résiliation d'un abonnement inexistant — redirige avec flash"""
def test_resiliation_abonnement_inexistant(auth_gestionnaire_client):
    response = auth_gestionnaire_client.post(
        '/subscriptions/99999/cancel',
        follow_redirects=True
    )
    assert response.status_code == 200

"""Cas 10 : Filtrage de la liste par statut"""
def test_liste_abonnements_avec_filtre(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/subscriptions/?status=ACTIF')
    assert response.status_code == 200

"""Cas 11 : Exception générale lors de la création d'abonnement"""
def test_creation_abonnement_exception_generale(auth_gestionnaire_client):
    response = auth_gestionnaire_client.post('/subscriptions/new', data={
        'student_id': 99999,
        'plan_id': 99999,
        'start_date': 'date-invalide',
        'end_date': 'date-invalide',
        'auto_renew': 'on'
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 12 : Exception générale (non-ValueError) lors de la création → flash "Erreur lors de la création"""
def test_creation_abonnement_exception_non_value_error(auth_gestionnaire_client, sample_student, sample_plan):
    with patch('app.routes.subscription_routes.SubscriptionService.create_subscription',
               side_effect=Exception("Erreur inattendue simulée")):
        response = auth_gestionnaire_client.post('/subscriptions/new', data={
            'student_id': sample_student.id,
            'plan_id': sample_plan.id,
            'start_date': '2026-10-01',
            'end_date': '2026-10-31',
            'auto_renew': 'on'
        }, follow_redirects=True)
    assert response.status_code == 200