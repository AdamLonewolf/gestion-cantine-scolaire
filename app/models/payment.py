from datetime import datetime, date
import uuid
from app import db

class Payment(db.Model):
    """Modèle Paiement d'un abonnement de cantine."""
    __tablename__ = 'payments'

    METHOD_ESPECES = 'ESPECES'
    METHOD_CARTE = 'CARTE'
    METHOD_VIREMENT = 'VIREMENT'
    METHOD_CHEQUE = 'CHEQUE'
    ALL_METHODS = [METHOD_ESPECES, METHOD_CARTE, METHOD_VIREMENT, METHOD_CHEQUE]

    STATUS_PAYE = 'PAYE'
    STATUS_EN_ATTENTE = 'EN_ATTENTE'
    STATUS_ANNULE = 'ANNULE'
    ALL_STATUSES = [STATUS_PAYE, STATUS_EN_ATTENTE, STATUS_ANNULE]

    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(20), nullable=False, default=METHOD_CARTE)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PAYE)
    reference = db.Column(db.String(64), unique=True, nullable=False, index=True)
    receipt_number = db.Column(db.String(64), unique=True, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def generate_reference():
        """Génère une référence unique pour le paiement."""
        return f"PAY-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def generate_receipt_number():
        """Génère un numéro de quittance/reçu unique."""
        return f"REC-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"

    def __repr__(self):
        return f'<Payment #{self.id} {self.reference} ({self.amount}€) [{self.status}]>'
