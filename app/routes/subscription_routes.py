from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.subscription import Subscription
from app.models.student import Student
from app.models.plan import SubscriptionPlan
from app.services.subscription_service import SubscriptionService
from app.routes.decorators import role_required
from app.models.user import User

subscription_bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

@subscription_bp.route('/')
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def list_subscriptions():
    """Liste de tous les abonnements avec filtres de statut."""
    status_filter = request.args.get('status', '').strip()
    query = Subscription.query.join(Student).join(SubscriptionPlan)

    if status_filter in Subscription.ALL_STATUSES:
        query = query.filter(Subscription.status == status_filter)

    subscriptions = query.order_by(Subscription.id.desc()).all()
    plans = SubscriptionPlan.query.all()
    return render_template(
        'subscriptions/list.html',
        subscriptions=subscriptions,
        status_filter=status_filter,
        statuses=Subscription.ALL_STATUSES,
        plans=plans
    )

@subscription_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def new_subscription():
    """Souscription d'un nouvel abonnement pour un étudiant."""
    selected_student_id = request.args.get('student_id', type=int)

    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        plan_id = request.form.get('plan_id', type=int)
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        auto_renew = bool(request.form.get('auto_renew'))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else date.today()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

            sub = SubscriptionService.create_subscription(
                student_id=student_id,
                plan_id=plan_id,
                start_date=start_date,
                end_date=end_date,
                auto_renew=auto_renew,
                status=Subscription.STATUS_EN_ATTENTE
            )
            flash(f"Abonnement #{sub.id} créé avec succès (Statut: {sub.status}). En attente de paiement.", "success")
            return redirect(url_for('students.student_detail', student_id=student_id))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erreur lors de la création : {str(e)}", "danger")

    students = Student.query.filter_by(is_active=True).order_by(Student.last_name.asc()).all()
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    today = date.today().strftime('%Y-%m-%d')

    return render_template(
        'subscriptions/form.html',
        students=students,
        plans=plans,
        selected_student_id=selected_student_id,
        today=today
    )

@subscription_bp.route('/<int:sub_id>/renew', methods=['POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def renew_subscription(sub_id):
    """Renouvellement manuel d'un abonnement."""
    try:
        new_sub = SubscriptionService.renew_subscription(sub_id)
        flash(f"Abonnement renouvelé avec succès pour la période suivante (Nouvel abonnement #{new_sub.id}).", "success")
        return redirect(url_for('students.student_detail', student_id=new_sub.student_id))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for('subscriptions.list_subscriptions'))

@subscription_bp.route('/<int:sub_id>/cancel', methods=['POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def cancel_subscription(sub_id):
    """Résiliation d'un abonnement."""
    try:
        sub = SubscriptionService.cancel_subscription(sub_id)
        flash(f"L'abonnement #{sub.id} a été résilié.", "warning")
        return redirect(url_for('students.student_detail', student_id=sub.student_id))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for('subscriptions.list_subscriptions'))
