from datetime import datetime, date
from app import db

class Student(db.Model):
    """Modèle Étudiant bénéficiaire de la cantine."""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    class_name = db.Column(db.String(50), nullable=False)  # ex: 'Terminale S', 'L1 Informatique'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    subscriptions = db.relationship('Subscription', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='student', lazy='dynamic')
    attendances = db.relationship('AttendanceLog', backref='student', lazy='dynamic')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_active_subscription(self, target_date=None):
        """Retourne l'abonnement actif couvrant la date spécifiée (ou aujourd'hui)."""
        if target_date is None:
            target_date = date.today()
        from app.models.subscription import Subscription
        return self.subscriptions.filter(
            Subscription.status == Subscription.STATUS_ACTIF,
            Subscription.start_date <= target_date,
            Subscription.end_date >= target_date
        ).first()

    def __repr__(self):
        return f'<Student {self.matricule} - {self.full_name}>'
