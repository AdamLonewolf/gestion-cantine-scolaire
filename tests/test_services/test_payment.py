import pytest
from app.services.payment_service import PaymentService
from app.models.subscription import Subscription

#Tests sur les paiements

"""
    CAS 1 : Un enregistrement fait avec un montant nul (0 euros)
"""
def test_payment_montant_nul(app, sample_subscription_en_attente):
    with pytest.raises(ValueError):
        PaymentService.record_payment(
            subscription_id=sample_subscription_en_attente.id,
            amount=0
        )


"""
    CAS 2 : Un enregistrement fait avec un montant négatif
"""
def test_payment_montant_negatif(app, sample_subscription_en_attente):
    with pytest.raises(ValueError):
        PaymentService.record_payment(
            subscription_id=sample_subscription_en_attente.id,
            amount=-10
        )


"""
    CAS 3 : Paiement fait de manière partielle (30 euros sur 60 euros)
"""
def test_payment_partiel(app, sample_subscription_en_attente):
   PaymentService.record_payment(
        subscription_id=sample_subscription_en_attente.id,
        amount=30  
    )
   assert sample_subscription_en_attente.status == Subscription.STATUS_EN_ATTENTE


"""
    CAS 4 : Paiement fait de manière intégrale (60 euros sur 60 euros)
"""
def test_payment_integral(app, sample_subscription_en_attente):
    PaymentService.record_payment(
        subscription_id=sample_subscription_en_attente.id,
        amount=60  
    )

"""Cas 5 : Suspension d'un abonnement actif non intégralement payé"""
def test_suspend_subscription_non_paye(app, sample_subscription_active):
    suspended = PaymentService.suspend_subscription_for_non_payment(
        sample_subscription_active.id
    )
    assert suspended.status == Subscription.STATUS_SUSPENDU

"""Cas 6 : Suspension d'un abonnement inexistant — lève une ValueError"""
def test_suspend_subscription_inexistant(app):
    with pytest.raises(ValueError):
        PaymentService.suspend_subscription_for_non_payment(99999)

"""Cas 7 : Mode de paiement invalide — lève une ValueError"""
def test_paiement_mode_invalide(app, sample_subscription_en_attente):
    with pytest.raises(ValueError):
        PaymentService.record_payment(
            subscription_id=sample_subscription_en_attente.id,
            amount=30,
            payment_method="CRYPTO"
        )

"""Cas 8 : Paiement sur abonnement inexistant — lève une ValueError"""
def test_paiement_abonnement_inexistant(app):
    with pytest.raises(ValueError):
        PaymentService.record_payment(
            subscription_id=99999,
            amount=60
        )

"""Cas 9 : Montant non numérique — lève une ValueError"""
def test_paiement_montant_non_numerique(app, sample_subscription_en_attente):
    with pytest.raises(ValueError):
        PaymentService.record_payment(
            subscription_id=sample_subscription_en_attente.id,
            amount="abc"
        )