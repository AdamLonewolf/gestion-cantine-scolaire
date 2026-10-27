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


"""Cas 5 : Résiliation d'un abonnement actif — statut passe à RESILIE"""
def test_cancel_subscription(app, sample_subscription_active):
    cancelled = SubscriptionService.cancel_subscription(
        sample_subscription_active.id
    )
    assert cancelled.status == Subscription.STATUS_RESILIE
    assert cancelled.auto_renew == False

"""Cas 6 : Résiliation d'un abonnement inexistant — lève une ValueError"""
def test_cancel_subscription_inexistant(app):
    with pytest.raises(ValueError):
        SubscriptionService.cancel_subscription(99999)

"""Cas 7 : Mise à jour des abonnements expirés — statut passe à EXPIRE"""
def test_update_expired_subscriptions(app, sample_subscription_active):
    from datetime import date, timedelta
    from app import db
    # Forcer la date de fin dans le passé
    sample_subscription_active.end_date = date.today() - timedelta(days=1)
    db.session.commit()

    count = SubscriptionService.update_expired_subscriptions()
    assert count >= 1
    assert sample_subscription_active.status == Subscription.STATUS_EXPIRE

"""Cas 8 : calculate_default_dates sans paramètre — retourne aujourd'hui + 30j"""
def test_calculate_default_dates_sans_parametre(app):
    from datetime import date, timedelta
    start, end = SubscriptionService.calculate_default_dates()
    assert start == date.today()
    assert end == date.today() + timedelta(days=30)

"""Cas 9 : check_overlap avec exclude_sub_id — exclut l'abonnement lui-même"""
def test_check_overlap_avec_exclusion(app, sample_subscription_active):
    # Exclure l'abonnement existant — ne doit pas détecter de chevauchement
    result = SubscriptionService.check_overlap(
        student_id=sample_subscription_active.student_id,
        start_date=sample_subscription_active.start_date,
        end_date=sample_subscription_active.end_date,
        exclude_sub_id=sample_subscription_active.id
    )
    assert result == False

"""Cas 10 : create_subscription avec statut invalide — lève une ValueError"""
def test_create_subscription_statut_invalide(app, sample_student, sample_plan):
    from datetime import date, timedelta
    with pytest.raises(ValueError):
        SubscriptionService.create_subscription(
            student_id=sample_student.id,
            plan_id=sample_plan.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status="STATUT_INEXISTANT"
        )

"""Cas 11 : renew_subscription sur un abonnement inexistant """
def test_renew_subscription_inexistant(app):
    with pytest.raises(ValueError):
        SubscriptionService.renew_subscription(99999)


# Cas 12 : student_id inexistant (étudiant introuvable)
def test_create_subscription_etudiant_inexistant(app, sample_plan):
    with pytest.raises(ValueError, match="Étudiant introuvable"):
        SubscriptionService.create_subscription(
            student_id=99999,
            plan_id=sample_plan.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )

# Cas 13 : plan_id inexistant
def test_create_subscription_plan_inexistant(app, sample_student):
    with pytest.raises(ValueError, match="Formule d'abonnement introuvable"):
        SubscriptionService.create_subscription(
            student_id=sample_student.id,
            plan_id=99999,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )

# Cas 14 : plan inactif (formule inactive)
def test_create_subscription_plan_inactif(app, sample_student):
    from app.models.plan import SubscriptionPlan
    from app import db
    plan_inactif = SubscriptionPlan(
        code="INACTIF_TEST",
        name="Plan Inactif",
        price_monthly=60.0,
        days_allowed="0,1,2,3,4",
        meals_per_day=1,
        is_active=False 
    )
    db.session.add(plan_inactif)
    db.session.commit()

    with pytest.raises(ValueError, match="n'est plus active"):
        SubscriptionService.create_subscription(
            student_id=sample_student.id,
            plan_id=plan_inactif.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )

# Cas 15 : end_date est égal à None  (calcul automatique de la date de fin)
def test_create_subscription_sans_end_date(app, sample_student, sample_plan):
    sub = SubscriptionService.create_subscription(
        student_id=sample_student.id,
        plan_id=sample_plan.id,
        start_date=date.today(),
        end_date=None  
    )
    assert sub is not None
    assert sub.end_date == date.today() + timedelta(days=30)


"""Cas 16 : create_subscription avec start_date=None — lève ValueError"""
def test_create_subscription_start_date_none(app, sample_student, sample_plan):
    with pytest.raises(ValueError):
        SubscriptionService.create_subscription(
            student_id=sample_student.id,
            plan_id=sample_plan.id,
            start_date=None,
            end_date=date.today() + timedelta(days=30)
        )