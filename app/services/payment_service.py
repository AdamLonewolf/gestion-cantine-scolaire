from datetime import date, datetime
from app import db
from app.models.subscription import Subscription
from app.models.payment import Payment

class PaymentService:
    """Service gérant les paiements et le contrôle des soldes."""

    @staticmethod
    def record_payment(subscription_id, amount, payment_method=Payment.METHOD_CARTE, notes=None, payment_date=None):
        """
        Enregistre un paiement pour un abonnement.
        RG-PAY-03 : Le montant ne peut être ni négatif ni nul.
        Dès que l'abonnement est intégralement réglé, il s'active automatiquement.
        """
        sub = db.session.get(Subscription, subscription_id)
        if not sub:
            raise ValueError("Abonnement introuvable.")

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Le montant saisi est invalide.")

        if amount <= 0:
            raise ValueError("Le montant du paiement doit être strictement supérieur à zéro.")

        if payment_method not in Payment.ALL_METHODS:
            raise ValueError(f"Méthode de paiement non reconnue: {payment_method}")

        if payment_date is None:
            payment_date = date.today()

        reference = Payment.generate_reference()
        receipt = Payment.generate_receipt_number()

        payment = Payment(
            subscription_id=sub.id,
            student_id=sub.student_id,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            status=Payment.STATUS_PAYE,
            reference=reference,
            receipt_number=receipt,
            notes=notes
        )
        db.session.add(payment)
        db.session.flush()

        # Si l'abonnement était en attente ou suspendu, vérifier si le solde est réglé
        # et activer l'abonnement si le montant total payé couvre le prix du forfait
        if sub.status in [Subscription.STATUS_EN_ATTENTE, Subscription.STATUS_SUSPENDU]:
            if sub.total_paid >= sub.plan.price_monthly:
                sub.status = Subscription.STATUS_ACTIF

        db.session.commit()
        return payment

    @staticmethod
    def suspend_subscription_for_non_payment(subscription_id):
        """RG-PAY-02 : Suspend un abonnement pour défaut de paiement."""
        sub = db.session.get(Subscription, subscription_id)
        if not sub:
            raise ValueError("Abonnement introuvable.")
        if sub.status == Subscription.STATUS_ACTIF and not sub.is_fully_paid:
            sub.status = Subscription.STATUS_SUSPENDU
            db.session.commit()
        return sub
