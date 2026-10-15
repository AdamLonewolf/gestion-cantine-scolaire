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


