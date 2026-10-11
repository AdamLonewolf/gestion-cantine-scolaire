from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.student import Student
from app.services.payment_service import PaymentService
from app.routes.decorators import role_required
from app.models.user import User

payment_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payment_bp.route('/')
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def list_payments():
    """Journal des paiements encaissés."""
    payments = Payment.query.order_by(Payment.id.desc()).all()
    total_amount = sum(p.amount for p in payments if p.status == Payment.STATUS_PAYE)
    return render_template('payments/list.html', payments=payments, total_amount=total_amount)

@payment_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def new_payment():
    """Enregistrement d'un règlement d'abonnement."""
    sub_id = request.args.get('subscription_id', type=int)
    student_id = request.args.get('student_id', type=int)

    selected_sub = db.session.get(Subscription, sub_id) if sub_id else None

    if request.method == 'POST':
        subscription_id = request.form.get('subscription_id', type=int)
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes')
        payment_date_str = request.form.get('payment_date')

        try:
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date() if payment_date_str else date.today()
            payment = PaymentService.record_payment(
                subscription_id=subscription_id,
                amount=amount,
                payment_method=payment_method,
                notes=notes,
                payment_date=payment_date
            )
            flash(
                f"Paiement de {payment.amount:.2f} € enregistré avec succès (Réf: {payment.reference}). "
                f"Statut abonnement mis à jour.",
                "success"
            )
            return redirect(url_for('payments.payment_receipt', payment_id=payment.id))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erreur d'encaissement : {str(e)}", "danger")

    # Recherche des abonnements non soldés ou en attente
    unpaid_subscriptions = Subscription.query.filter(
        Subscription.status.in_([Subscription.STATUS_EN_ATTENTE, Subscription.STATUS_SUSPENDU, Subscription.STATUS_ACTIF])
    ).all()

    today = date.today().strftime('%Y-%m-%d')
    return render_template(
        'payments/form.html',
        unpaid_subscriptions=unpaid_subscriptions,
        selected_sub=selected_sub,
        methods=Payment.ALL_METHODS,
        today=today
    )

@payment_bp.route('/<int:payment_id>/receipt')
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def payment_receipt(payment_id):
    """Quittance / Reçu de paiement imprimable."""
    payment = db.session.get(Payment, payment_id)
    if not payment:
        flash("Paiement introuvable.", "danger")
        return redirect(url_for('payments.list_payments'))
    return render_template('payments/receipt.html', payment=payment)
