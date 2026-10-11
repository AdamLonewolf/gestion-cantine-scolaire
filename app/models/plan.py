from datetime import datetime
from app import db

class SubscriptionPlan(db.Model):
    """Modèle Formule / Forfait d'abonnement cantine."""
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price_monthly = db.Column(db.Float, nullable=False)  # ex: 60.00 EUR
    # Jours autorisés sous forme d'entiers séparés par des virgules (0=Lundi, 1=Mardi, ..., 6=Dimanche)
    days_allowed = db.Column(db.String(20), nullable=False, default="0,1,2,3,4")
    # Repas autorisés par jour : 1 (Midi uniquement) ou 2 (Midi + Soir)
    meals_per_day = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relation vers abonnements
    subscriptions = db.relationship('Subscription', backref='plan', lazy='dynamic')

    def is_day_allowed(self, target_date):
        """Vérifie si le jour de la semaine (0=Lundi, ..., 6=Dimanche) est inclus dans le forfait."""
        allowed_weekdays = [int(x.strip()) for x in self.days_allowed.split(',') if x.strip()]
        return target_date.weekday() in allowed_weekdays

    @property
    def days_allowed_labels(self):
        """Retourne la liste textuelle des jours autorisés."""
        names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        allowed = [int(x.strip()) for x in self.days_allowed.split(',') if x.strip()]
        return ", ".join(names[i] for i in allowed if 0 <= i <= 6)

    def __repr__(self):
        return f'<SubscriptionPlan {self.code} - {self.name} ({self.price_monthly}€)>'
