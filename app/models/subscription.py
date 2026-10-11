from datetime import datetime, date
from app import db

class Subscription(db.Model):
    """Modèle Abonnement mensuel renouvelable d'un étudiant."""
    __tablename__ = 'subscriptions'

    STATUS_EN_ATTENTE = 'EN_ATTENTE_PAIEMENT'
    STATUS_ACTIF = 'ACTIF'
    STATUS_SUSPENDU = 'SUSPENDU'
    STATUS_EXPIRE = 'EXPIRE'
    STATUS_RESILIE = 'RESILIE'

    ALL_STATUSES = [
        STATUS_EN_ATTENTE,
        STATUS_ACTIF,
        STATUS_SUSPENDU,
        STATUS_EXPIRE,
        STATUS_RESILIE
    ]

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), nullable=False, default=STATUS_EN_ATTENTE)
    auto_renew = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    payments = db.relationship('Payment', backref='subscription', lazy='dynamic')

    @property
    def is_currently_valid(self):
        """Vérifie si l'abonnement est actif et valide à la date d'aujourd'hui."""
        today = date.today()
        return self.is_valid_on(today)

    def is_valid_on(self, target_date):
        """Vérifie si l'abonnement est actif et couvre la date donnée."""
        return (
            self.status == self.STATUS_ACTIF and
            self.start_date <= target_date <= self.end_date
        )

    @property
    def total_paid(self):
        """Somme des paiements validés pour cet abonnement."""
        from app.models.payment import Payment
        paid_sum = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.subscription_id == self.id,
            Payment.status == Payment.STATUS_PAYE
        ).scalar()
        return paid_sum or 0.0

    @property
    def balance_due(self):
        """Montant restant dû sur cet abonnement."""
        expected = self.plan.price_monthly if self.plan else 0.0
        return max(0.0, expected - self.total_paid)

    @property
    def is_fully_paid(self):
        return self.balance_due <= 0.0

    def __repr__(self):
        return f'<Subscription #{self.id} Student:{self.student_id} Plan:{self.plan_id} [{self.status}]>'
