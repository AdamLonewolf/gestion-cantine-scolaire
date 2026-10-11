from datetime import date, timedelta
from app import db
from app.models.student import Student
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription

class SubscriptionService:
    """Service gérant la souscription et le renouvellement des abonnements."""

    @staticmethod
    def calculate_default_dates(start_date=None):
        """
        Calcule les dates par défaut pour un mois calendaire :
        Du jour spécifié (ou aujourd'hui) jusqu'à J+30 jours.
        """
        if start_date is None:
            start_date = date.today()
        # Durée standard de 30 jours (ou mois suivant - 1 jour)
        end_date = start_date + timedelta(days=30)
        return start_date, end_date

    @staticmethod
    def check_overlap(student_id, start_date, end_date, exclude_sub_id=None):
        """
        RG-ABO-02 : Interdiction de chevauchement de périodes pour un même étudiant
        sur des abonnements actifs ou en attente.
        """
        query = Subscription.query.filter(
            Subscription.student_id == student_id,
            Subscription.status.in_([Subscription.STATUS_ACTIF, Subscription.STATUS_EN_ATTENTE]),
            Subscription.start_date <= end_date,
            Subscription.end_date >= start_date
        )
        if exclude_sub_id:
            query = query.filter(Subscription.id != exclude_sub_id)

        overlapping = query.first()
        return overlapping is not None

    @staticmethod
    def create_subscription(student_id, plan_id, start_date, end_date=None, auto_renew=True, status=Subscription.STATUS_EN_ATTENTE):
        """
        Crée un abonnement pour un étudiant en validant les contraintes métier.
        """
        # Vérification de l'étudiant
        student = db.session.get(Student, student_id)
        if not student:
            raise ValueError("Étudiant introuvable.")
        if not student.is_active:
            raise ValueError("Impossible de souscrire un abonnement pour un étudiant inactif.")

        # Vérification de la formule
        plan = db.session.get(SubscriptionPlan, plan_id)
        if not plan:
            raise ValueError("Formule d'abonnement introuvable.")
        if not plan.is_active:
            raise ValueError("Cette formule d'abonnement n'est plus active.")

        # Validation des dates
        if not start_date:
            raise ValueError("La date de début est obligatoire.")

        if not end_date:
            end_date = start_date + timedelta(days=30)

        if end_date < start_date:
            raise ValueError("La date de fin ne peut pas être antérieure à la date de début.")

        # RG-ABO-02 : Vérification du chevauchement
        if SubscriptionService.check_overlap(student_id, start_date, end_date):
            raise ValueError(
                f"Chevauchement interdit : l'étudiant possède déjà un abonnement actif ou en attente couvrant cette période "
                f"({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})."
            )

        if status not in Subscription.ALL_STATUSES:
            raise ValueError(f"Statut d'abonnement invalide: {status}")

        subscription = Subscription(
            student_id=student_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            auto_renew=auto_renew
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription

    @staticmethod
    def renew_subscription(subscription_id):
        """
        RG-ABO-03 : Renouvellement d'un abonnement mensuel pour la période suivante.
        """
        sub = db.session.get(Subscription, subscription_id)
        if not sub:
            raise ValueError("Abonnement introuvable.")

        # La nouvelle période débute le lendemain de la fin précédente
        new_start = sub.end_date + timedelta(days=1)
        new_end = new_start + timedelta(days=30)

        # Création du nouvel abonnement en attente de paiement
        return SubscriptionService.create_subscription(
            student_id=sub.student_id,
            plan_id=sub.plan_id,
            start_date=new_start,
            end_date=new_end,
            auto_renew=sub.auto_renew,
            status=Subscription.STATUS_EN_ATTENTE
        )

    @staticmethod
    def cancel_subscription(subscription_id):
        """Résilie un abonnement."""
        sub = db.session.get(Subscription, subscription_id)
        if not sub:
            raise ValueError("Abonnement introuvable.")
        sub.status = Subscription.STATUS_RESILIE
        sub.auto_renew = False
        db.session.commit()
        return sub

    @staticmethod
    def update_expired_subscriptions():
        """Met à jour les abonnements dont la date de fin est dépassée."""
        today = date.today()
        expired = Subscription.query.filter(
            Subscription.status == Subscription.STATUS_ACTIF,
            Subscription.end_date < today
        ).all()
        for sub in expired:
            sub.status = Subscription.STATUS_EXPIRE
        db.session.commit()
        return len(expired)
