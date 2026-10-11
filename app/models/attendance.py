from datetime import datetime
from app import db

class AttendanceLog(db.Model):
    """Journal des pointages et fréquentations au réfectoire."""
    __tablename__ = 'attendance_logs'

    SERVICE_DEJEUNER = 'DEJEUNER'
    SERVICE_DINER = 'DINER'
    SERVICES = [SERVICE_DEJEUNER, SERVICE_DINER]

    STATUS_AUTORISE = 'AUTORISE'
    STATUS_REFUSE = 'REFUSE'
    STATUSES = [STATUS_AUTORISE, STATUS_REFUSE]

    REASON_STUDENT_INACTIVE = 'ETUDIANT_INACTIF'
    REASON_NO_SUBSCRIPTION = 'PAS_D_ABONNEMENT'
    REASON_EXPIRED = 'ABONNEMENT_EXPIRE'
    REASON_SUSPENDED = 'IMPAYE_SUSPENDU'
    REASON_SUSPENDU = 'IMPAYE_SUSPENDU'
    REASON_DAY_NOT_ALLOWED = 'JOUR_NON_AUTORISE'
    REASON_OUT_OF_HOURS = 'HORS_CRENEAU'
    REASON_ALREADY_USED = 'DEJA_CONSOMME'
    REASON_NOT_ENOUGH_MEALS = 'REPAS_EPUISE'

    REASONS = [
        REASON_STUDENT_INACTIVE,
        REASON_NO_SUBSCRIPTION,
        REASON_EXPIRED,
        REASON_SUSPENDED,
        REASON_DAY_NOT_ALLOWED,
        REASON_OUT_OF_HOURS,
        REASON_ALREADY_USED,
        REASON_NOT_ENOUGH_MEALS
    ]

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    service_type = db.Column(db.String(20), nullable=False, default=SERVICE_DEJEUNER)
    status = db.Column(db.String(20), nullable=False)
    refusal_reason = db.Column(db.String(50), nullable=True)
    scanned_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relation vers l'agent qui a scanné/pointé
    scanned_by = db.relationship('User', backref='scanned_attendances')

    @property
    def is_authorized(self):
        return self.status == self.STATUS_AUTORISE

    @property
    def formatted_time(self):
        return self.timestamp.strftime('%H:%M:%S')

    @property
    def formatted_date(self):
        return self.timestamp.strftime('%d/%m/%Y')

    def __repr__(self):
        return f'<Attendance #{self.id} Student:{self.student_id} [{self.status}] at {self.timestamp}>'
