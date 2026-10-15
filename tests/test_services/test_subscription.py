import pytest
from datetime import date, timedelta
from app.services.subscription_service import SubscriptionService
from app.models.subscription import Subscription

#Tests sur les Abonnements 

"""
    CAS 1 : Une souscription avec end_date < start_date est rejetée 
"""
def test_subscription_date_invalide(app, sample_student, sample_plan):
    start = date.today()
    end = date.today() - timedelta(days=5)
    with pytest.raises(ValueError):
        SubscriptionService.create_subscription(
            student_id=sample_student.id,
            plan_id=sample_plan.id,
            start_date=start,
            end_date=end
        )


"""
    CAS 2 : renouveler un abonnement expiré crée un nouvel abonnement au statut EN_ATTENTE_PAIEMENT
"""
def test_subscription_expired_renew(sample_subscription_expire) : 
    nouvel_abo = SubscriptionService.renew_subscription(sample_subscription_expire.id)
    assert nouvel_abo.status == Subscription.STATUS_EN_ATTENTE
    assert nouvel_abo.start_date == sample_subscription_expire.end_date + timedelta(days=1)


"""
    CAS 3 : créer deux abonnements dont les plages de
    dates se chevauchent s'ils sont à l'état ACTIF ou EN_ATTENTE_PAIEMENT retourne une erreur (interdit)
"""
def test_chevauchement_subscription(sample_plan, sample_student, sample_subscription_active) : 
    with pytest.raises(ValueError):
        SubscriptionService.create_subscription(
            student_id=sample_student.id,
            plan_id=sample_plan.id,
            start_date=date.today(),     
            end_date=date.today() + timedelta(days=15)
        )


           