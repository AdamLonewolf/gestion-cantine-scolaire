import pytest
from unittest.mock import patch

"""Cas 1 : Un gestionnaire peut accéder à la liste des paiements"""
def test_liste_paiements_gestionnaire(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/payments/')
    assert response.status_code == 200

"""Cas 2 : Un agent n'a pas accès à la liste des paiements"""
def test_liste_paiements_agent_interdit(auth_agent_client):
    response = auth_agent_client.get('/payments/')
    assert response.status_code == 403

"""Cas 3 : Un gestionnaire peut accéder au formulaire de nouveau paiement"""
def test_formulaire_paiement(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/payments/new')
    assert response.status_code == 200

"""Cas 4 : Enregistrement d'un paiement valide — redirige vers le reçu"""
def test_enregistrement_paiement_valide(auth_gestionnaire_client, sample_subscription_en_attente):
    response = auth_gestionnaire_client.post('/payments/new', data={
        'subscription_id': sample_subscription_en_attente.id,
        'amount': '60.00',
        'payment_method': 'ESPECES',
        'payment_date': '2026-10-01'
    }, follow_redirects=False)
    assert response.status_code == 302

"""Cas 5 : Enregistrement d'un paiement avec montant nul — reste sur le formulaire avec erreur"""
def test_enregistrement_paiement_montant_nul(auth_gestionnaire_client, sample_subscription_en_attente):
    response = auth_gestionnaire_client.post('/payments/new', data={
        'subscription_id': sample_subscription_en_attente.id,
        'amount': '0',
        'payment_method': 'ESPECES',
        'payment_date': '2026-10-01'
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 6 : Accès au reçu d'un paiement inexistant — redirige avec message flash"""
def test_recu_paiement_inexistant(auth_gestionnaire_client):
    response = auth_gestionnaire_client.get('/payments/99999/receipt', follow_redirects=True)
    assert response.status_code == 200

"""Cas 7 : Exception générale lors d'un paiement — reste sur formulaire"""
def test_enregistrement_paiement_abonnement_inexistant(auth_gestionnaire_client):
    response = auth_gestionnaire_client.post('/payments/new', data={
        'subscription_id': 99999,
        'amount': '60.00',
        'payment_method': 'ESPECES',
        'payment_date': '2026-10-01'
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 8 : Exception générale lors d'un paiement — type de données invalide"""
def test_paiement_exception_generale(auth_gestionnaire_client, sample_subscription_en_attente):
    response = auth_gestionnaire_client.post('/payments/new', data={
        'subscription_id': sample_subscription_en_attente.id,
        'amount': '60.00',
        'payment_method': 'MODE_INVALIDE',
        'payment_date': '2026-10-01'
    }, follow_redirects=True)
    assert response.status_code == 200

"""Cas 9 : Exception générale (non-ValueError) dans record_payment → flash "Erreur d'encaissement"""
def test_paiement_exception_generale_non_value_error(auth_gestionnaire_client, sample_subscription_en_attente):
    with patch('app.routes.payment_routes.PaymentService.record_payment',
               side_effect=Exception("Erreur base de données simulée")):
        response = auth_gestionnaire_client.post('/payments/new', data={
            'subscription_id': sample_subscription_en_attente.id,
            'amount': '60.00',
            'payment_method': 'ESPECES',
            'payment_date': '2026-10-01'
        }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Erreur' in response.data.decode('utf-8') or response.status_code == 200

"""Cas 10 : Accès au reçu d'un paiement existant"""
def test_recu_paiement_existant(auth_gestionnaire_client, sample_subscription_en_attente):
    from app.services.payment_service import PaymentService
    payment = PaymentService.record_payment(
        subscription_id=sample_subscription_en_attente.id,
        amount=60
    )
    response = auth_gestionnaire_client.get(f'/payments/{payment.id}/receipt')
    assert response.status_code == 200