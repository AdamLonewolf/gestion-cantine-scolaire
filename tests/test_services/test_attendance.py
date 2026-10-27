import pytest
from app.services.attendance_service import AttendanceService
from app.models.attendance import AttendanceLog
from datetime import datetime, date, timedelta
from app.models.subscription import Subscription
from app import db

#Tests sur les fréquentations (Passages au refectoire)

"""CAS 1 : Passage Autorisé """
def test_passage_autorise(app, sample_student, sample_subscription_active):
    from datetime import datetime, timedelta
    today = date.today()
    days_since_monday = today.weekday()
    if days_since_monday >= 5: 
        monday = today + timedelta(days=(7 - days_since_monday))
    else:
        monday = today

    check_datetime = datetime.combine(monday, datetime.min.time().replace(hour=12))

    # Adapter aussi l'abonnement pour couvrir ce lundi
    sample_subscription_active.start_date = monday
    sample_subscription_active.end_date = monday + timedelta(days=30)
    from app import db
    db.session.commit()

    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_datetime
    )
    assert is_authorized == True
    assert log.status == AttendanceLog.STATUS_AUTORISE


"""CAS 2 : Passage refusé """
def test_passage_refuse(app, sample_student, sample_subscription_active):
    today = date.today()
    days_since_monday = today.weekday()
    if days_since_monday >= 5:
        monday = today + timedelta(days=(7 - days_since_monday))
    else:
        monday = today

    check_datetime = datetime.combine(monday, datetime.min.time().replace(hour=12))

    # Adapter l'abonnement
    sample_subscription_active.start_date = monday
    sample_subscription_active.end_date = monday + timedelta(days=30)
    db.session.commit()

    # Premier passage
    AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_datetime
    )
    # Deuxième passage — même heure
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_datetime
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_ALREADY_USED


"""CAS 3 : Abonnement suspendu """
def test_passage_subscription_suspended(app, sample_student,sample_subscription_suspendu):
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_SUSPENDU


"""Cas 4 : Abonnement Expiré"""
def test_passage_subscription_expired(app, sample_student,sample_subscription_expire):
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_EXPIRED


"""Cas 5 : Sans Abonnement """
def test_passage_sans_subscription(app, sample_student):
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_NO_SUBSCRIPTION


"""Cas 6 : Étudiant inactif """
def test_passage_etudiant_inactif(app, sample_student_inactif):
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student_inactif.matricule
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_STUDENT_INACTIVE

"""Cas 7 : Passage lors d'un jour non autorisé (Forfait 4j - Lundi, Mardi, Jeudi, Vendredi - SANS Mercredi)"""
def test_passage_jour_non_autorise(app, sample_student,sample_plan_4j):
    #On crée un Abonnement avec le plan 4J
    sub = Subscription(
        student_id=sample_student.id,
        plan_id=sample_plan_4j.id,
        start_date=date.today() - timedelta(days=5),
        end_date=date.today() + timedelta(days=25),
        status=Subscription.STATUS_ACTIF,
        auto_renew=True
    )
    db.session.add(sub)
    db.session.commit()

    # Trouver le prochain mercredi 
    today = date.today()
    days_until_wednesday = (2 - today.weekday()) % 7
    if days_until_wednesday == 0:
        days_until_wednesday = 7
    wednesday = today + timedelta(days=days_until_wednesday)
    check_datetime = datetime.combine(wednesday, datetime.min.time().replace(hour=12))

    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_datetime
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_DAY_NOT_ALLOWED

    """Cas 8 : Passage hors créneau horaire avec enforce_hours activé"""
def test_passage_hors_horaire(app, sample_student, sample_subscription_active):
    from datetime import datetime, date, timedelta
    # Forcer un lundi à 3h du matin (hors créneau déjeuner et dîner)
    today = date.today()
    days_since_monday = today.weekday()
    monday = today if days_since_monday < 5 else today + timedelta(days=7 - days_since_monday)
    check_datetime = datetime.combine(monday, datetime.min.time().replace(hour=3))

    sample_subscription_active.start_date = monday
    sample_subscription_active.end_date = monday + timedelta(days=30)
    db.session.commit()

    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_datetime,
        enforce_hours=True
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_OUT_OF_HOURS

"""Cas 9 : Passage avec abonnement EN_ATTENTE_PAIEMENT — refus"""
def test_passage_abonnement_en_attente(app, sample_student, sample_subscription_en_attente):
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False

"""Cas 10 : determine_service_type après 16h retourne DINER"""
def test_determine_service_type_diner(app):
    from datetime import datetime
    check_time = datetime.now().replace(hour=19)
    result = AttendanceService.determine_service_type(check_time)
    assert result == AttendanceLog.SERVICE_DINER

"""Cas 11 : Abonnement EN_ATTENTE sur la période — motif SUSPENDU"""
def test_passage_abonnement_non_actif_autre_statut(app, sample_student, sample_plan):
    sub = Subscription(
        student_id=sample_student.id,
        plan_id=sample_plan.id,
        start_date=date.today() - timedelta(days=5),
        end_date=date.today() + timedelta(days=25),
        status=Subscription.STATUS_EN_ATTENTE,
        auto_renew=True
    )
    db.session.add(sub)
    db.session.commit()
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_SUSPENDU


    # Cas 12 :  déjeuner déjà pris (REASON_NOT_ENOUGH_MEALS)
def test_passage_repas_epuise(app, sample_student, sample_plan, sample_subscription_active):
    from datetime import datetime, date, timedelta

    today = date.today()
    days_since_monday = today.weekday()
    monday = today if days_since_monday < 5 else today + timedelta(days=7 - days_since_monday)

    # S'assurer que l'abonnement couvre ce lundi
    sample_subscription_active.start_date = monday
    sample_subscription_active.end_date = monday + timedelta(days=30)
    db.session.commit()

    # Premier passage : déjeuner → autorisé
    check_dejeuner = datetime.combine(monday, datetime.min.time().replace(hour=12))
    AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_dejeuner
    )

    # Deuxième passage : dîner le même jour → refus car meals_per_day=1
    check_diner = datetime.combine(monday, datetime.min.time().replace(hour=19))
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_diner,
        service_type='DINER'
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_NOT_ENOUGH_MEALS

# Cas 13 : abonnement EN_ATTENTE couvrant la période refus avec motif SUSPENDU

def test_passage_abonnement_en_attente_couvrant_periode(app, sample_student, sample_plan):
    from datetime import date, timedelta
    from app.models.subscription import Subscription
    from app import db

    sub = Subscription(
        student_id=sample_student.id,
        plan_id=sample_plan.id,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        status=Subscription.STATUS_EN_ATTENTE,
        auto_renew=True
    )
    db.session.add(sub)
    db.session.commit()

    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_SUSPENDU


"""Cas 14 : Abonnement RESILIE sur la période — motif NO_SUBSCRIPTION"""
def test_passage_abonnement_resilie(app, sample_student, sample_plan):
    from app.models.subscription import Subscription
    sub = Subscription(
        student_id=sample_student.id,
        plan_id=sample_plan.id,
        start_date=date.today() - timedelta(days=5),
        end_date=date.today() + timedelta(days=25),
        status=Subscription.STATUS_RESILIE,
        auto_renew=False
    )
    db.session.add(sub)
    db.session.commit()

    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False
    assert log.refusal_reason == AttendanceLog.REASON_NO_SUBSCRIPTION