import pytest
from datetime import date, timedelta
from app.models.attendance import AttendanceLog
from app.models.subscription import Subscription
from app.models.plan import SubscriptionPlan
from app.models.student import Student
from app.models.payment import Payment
from app import db

"""Cas 1 : is_authorized retourne True pour un log AUTORISE"""
def test_attendance_is_authorized(app, sample_student, sample_subscription_active):
    log = AttendanceLog(
        student_id=sample_student.id,
        timestamp=__import__('datetime').datetime.now(),
        service_type=AttendanceLog.SERVICE_DEJEUNER,
        status=AttendanceLog.STATUS_AUTORISE
    )
    db.session.add(log)
    db.session.commit()
    assert log.is_authorized == True

"""Cas 2 : formatted_date retourne la date au bon format"""
def test_attendance_formatted_date(app, sample_student):
    from datetime import datetime
    log = AttendanceLog(
        student_id=sample_student.id,
        timestamp=datetime(2026, 10, 18, 12, 0, 0),
        service_type=AttendanceLog.SERVICE_DEJEUNER,
        status=AttendanceLog.STATUS_AUTORISE
    )
    db.session.add(log)
    db.session.commit()
    assert log.formatted_date == "18/10/2026"

"""Cas 3 : is_currently_valid retourne True pour un abonnement actif aujourd'hui"""
def test_subscription_is_currently_valid(app, sample_subscription_active):
    assert sample_subscription_active.is_currently_valid == True

"""Cas 4 : is_valid_on retourne False pour un abonnement expiré"""
def test_subscription_is_valid_on_expired(app, sample_subscription_expire):
    assert sample_subscription_expire.is_valid_on(date.today()) == False

"""Cas 5 : days_allowed_labels retourne les bons labels"""
def test_plan_days_allowed_labels(app, sample_plan):
    labels = sample_plan.days_allowed_labels
    assert "Lun" in labels

"""Cas 6 : __repr__ du plan"""
def test_plan_repr(app, sample_plan):
    assert "TEST_5J" in repr(sample_plan)

"""Cas 7 : check_password retourne False si pas de hash"""
def test_user_check_password_sans_hash(app, admin_user):
    admin_user.password_hash = None
    assert admin_user.check_password("Password123!") == False

"""Cas 8 : is_agent retourne True pour un agent"""
def test_user_is_agent(app, agent_user):
    assert agent_user.is_agent == True

"""Cas 9 : __repr__ du student"""
def test_student_repr(app, sample_student):
    assert "ETU-99001" in repr(sample_student)

"""Cas 10 : __repr__ du payment"""
def test_payment_repr(app, sample_subscription_en_attente):
    from app.services.payment_service import PaymentService
    payment = PaymentService.record_payment(
        subscription_id=sample_subscription_en_attente.id,
        amount=60
    )
    assert "PAY-" in repr(payment)

"""Cas 11 : __repr__ du User"""
def test_user_repr(app, admin_user):
    assert "admin_test" in repr(admin_user)

"""Cas 12 : __repr__ de Subscription"""
def test_subscription_repr(app, sample_subscription_active):
    assert "Subscription" in repr(sample_subscription_active)

"""Cas 13 : __repr__ de AttendanceLog"""
def test_attendance_repr(app, sample_student, sample_subscription_active):
    from app.services.attendance_service import AttendanceService
    from datetime import date, timedelta
    today = date.today()
    days_since_monday = today.weekday()
    monday = today if days_since_monday < 5 else today + timedelta(days=7 - days_since_monday)
    from datetime import datetime
    check_datetime = datetime.combine(monday, datetime.min.time().replace(hour=12))
    sample_subscription_active.start_date = monday
    sample_subscription_active.end_date = monday + timedelta(days=30)
    db.session.commit()
    is_auth, log, student, msg = AttendanceService.process_check_in(
        matricule=sample_student.matricule,
        check_datetime=check_datetime
    )
    assert "Attendance" in repr(log)