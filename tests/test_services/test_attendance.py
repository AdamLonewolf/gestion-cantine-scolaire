import pytest
from app.services.attendance_service import AttendanceService
from app.models.attendance import AttendanceLog
from datetime import datetime, date, timedelta
from app.models.subscription import Subscription
from app import db
#Tests sur les fréquentations (Passages au refectoire)

"""CAS 1 : Passage Autorisé """
def test_passage_autorise(app, sample_subscription_active, sample_student):
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == True
    assert log.status == AttendanceLog.STATUS_AUTORISE


"""CAS 2 : Passage Autorisé """
def test_passage_refuse(app, sample_student, sample_subscription_active):
    #Premier passage de l'étudiant
    AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    #Deuxième passage de l'étudiant
    is_authorized, log, student, message = AttendanceService.process_check_in(
        matricule=sample_student.matricule
    )
    assert is_authorized == False
    assert log.status == AttendanceLog.STATUS_REFUSE


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