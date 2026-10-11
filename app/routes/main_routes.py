from datetime import datetime, date, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models.student import Student
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.attendance import AttendanceLog

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Tableau de bord principal de la cantine scolaire."""
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # Statistiques globales
    total_students = Student.query.count()
    active_students = Student.query.filter_by(is_active=True).count()

    active_subscriptions = Subscription.query.filter(
        Subscription.status == Subscription.STATUS_ACTIF,
        Subscription.start_date <= today,
        Subscription.end_date >= today
    ).count()

    pending_subscriptions = Subscription.query.filter(
        Subscription.status.in_([Subscription.STATUS_EN_ATTENTE, Subscription.STATUS_SUSPENDU])
    ).count()

    # Passages du jour
    today_attendances = AttendanceLog.query.filter(
        AttendanceLog.timestamp >= start_of_day,
        AttendanceLog.timestamp <= end_of_day
    ).all()

    today_authorized = sum(1 for a in today_attendances if a.is_authorized)
    today_rejected = sum(1 for a in today_attendances if not a.is_authorized)

    # Abonnements expirant dans les 7 prochains jours
    in_7_days = today + timedelta(days=7)
    expiring_soon = Subscription.query.filter(
        Subscription.status == Subscription.STATUS_ACTIF,
        Subscription.end_date >= today,
        Subscription.end_date <= in_7_days
    ).order_by(Subscription.end_date.asc()).limit(5).all()

    # Derniers passages
    recent_attendances = AttendanceLog.query.order_by(
        AttendanceLog.timestamp.desc()
    ).limit(8).all()

    # Total des encaissements du mois en cours
    first_day_month = today.replace(day=1)
    total_revenue_month = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == Payment.STATUS_PAYE,
        Payment.payment_date >= first_day_month
    ).scalar() or 0.0

    return render_template(
        'dashboard.html',
        total_students=total_students,
        active_students=active_students,
        active_subscriptions=active_subscriptions,
        pending_subscriptions=pending_subscriptions,
        today_authorized=today_authorized,
        today_rejected=today_rejected,
        expiring_soon=expiring_soon,
        recent_attendances=recent_attendances,
        total_revenue_month=total_revenue_month,
        today_date=today.strftime('%d/%m/%Y')
    )
