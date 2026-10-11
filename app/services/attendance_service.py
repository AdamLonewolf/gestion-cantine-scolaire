from datetime import datetime, date, time
from app import db
from app.models.student import Student
from app.models.subscription import Subscription
from app.models.attendance import AttendanceLog

class AttendanceService:
    """Service gérant le pointage et le contrôle d'accès au réfectoire."""

    @staticmethod
    def determine_service_type(check_time):
        """Détermine le type de service (Déjeuner ou Dîner) selon l'heure."""
        hour = check_time.hour
        # Par convention : Avant 16h = DEJEUNER, Après 16h = DINER
        if hour < 16:
            return AttendanceLog.SERVICE_DEJEUNER
        return AttendanceLog.SERVICE_DINER

    @staticmethod
    def process_check_in(matricule, scanned_by_user_id=None, check_datetime=None, service_type=None, enforce_hours=False):
        """
        Algorithme de contrôle d'accès au réfectoire (RG-FRQ-01 à RG-FRQ-04).
        Retourne (is_authorized: bool, log: AttendanceLog, student: Student, message: str)
        """
        if check_datetime is None:
            check_datetime = datetime.now()

        check_date = check_datetime.date()
        matricule = (matricule or "").strip().upper()

        if not service_type:
            service_type = AttendanceService.determine_service_type(check_datetime)

        # 1. Recherche de l'étudiant
        student = Student.query.filter_by(matricule=matricule).first()
        if not student:
            # Pas d'étudiant correspondant
            return False, None, None, f"Aucun étudiant trouvé avec le matricule '{matricule}'."

        # 2. Vérification statut étudiant (RG-ETU-03)
        if not student.is_active:
            log = AttendanceService._record_log(
                student_id=student.id,
                timestamp=check_datetime,
                service_type=service_type,
                status=AttendanceLog.STATUS_REFUSE,
                reason=AttendanceLog.REASON_STUDENT_INACTIVE,
                scanned_by=scanned_by_user_id
            )
            return False, log, student, "Accès refusé : Le dossier de l'étudiant est inactif."

        # 3. Vérification des créneaux horaires (si activé)
        if enforce_hours:
            current_time = check_datetime.time()
            lunch_start, lunch_end = time(11, 30), time(14, 0)
            dinner_start, dinner_end = time(18, 30), time(20, 30)

            is_lunch_time = (service_type == AttendanceLog.SERVICE_DEJEUNER and lunch_start <= current_time <= lunch_end)
            is_dinner_time = (service_type == AttendanceLog.SERVICE_DINER and dinner_start <= current_time <= dinner_end)

            if not (is_lunch_time or is_dinner_time):
                log = AttendanceService._record_log(
                    student_id=student.id,
                    timestamp=check_datetime,
                    service_type=service_type,
                    status=AttendanceLog.STATUS_REFUSE,
                    reason=AttendanceLog.REASON_OUT_OF_HOURS,
                    scanned_by=scanned_by_user_id
                )
                return False, log, student, "Accès refusé : Le réfectoire est actuellement fermé."

        # 4. Vérification de l'abonnement
        # Recherche d'un abonnement couvrant la date courante (quel que soit son statut pour motif précis)
        all_subs = Subscription.query.filter(
            Subscription.student_id == student.id,
            Subscription.start_date <= check_date,
            Subscription.end_date >= check_date
        ).all()

        if not all_subs:
            # Vérifier si l'étudiant a eu un abonnement dans le passé mais qui est maintenant expiré
            past_sub = Subscription.query.filter(
                Subscription.student_id == student.id,
                Subscription.end_date < check_date
            ).order_by(Subscription.end_date.desc()).first()

            reason = AttendanceLog.REASON_EXPIRED if past_sub else AttendanceLog.REASON_NO_SUBSCRIPTION
            msg = "Accès refusé : Abonnement mensuel expiré." if past_sub else "Accès refusé : Aucun abonnement souscrit."

            log = AttendanceService._record_log(
                student_id=student.id,
                timestamp=check_datetime,
                service_type=service_type,
                status=AttendanceLog.STATUS_REFUSE,
                reason=reason,
                scanned_by=scanned_by_user_id
            )
            return False, log, student, msg

        # Prendre l'abonnement pour la période
        active_sub = next((s for s in all_subs if s.status == Subscription.STATUS_ACTIF), None)

        if not active_sub:
            sub = all_subs[0]
            if sub.status == Subscription.STATUS_SUSPENDU:
                reason = AttendanceLog.REASON_SUSPENDU
                msg = "Accès refusé : Abonnement suspendu pour impayé."
            elif sub.status == Subscription.STATUS_EN_ATTENTE:
                reason = AttendanceLog.REASON_SUSPENDU
                msg = "Accès refusé : Abonnement en attente de paiement."
            else:
                reason = AttendanceLog.REASON_NO_SUBSCRIPTION
                msg = f"Accès refusé : Abonnement non actif ({sub.status})."

            log = AttendanceService._record_log(
                student_id=student.id,
                timestamp=check_datetime,
                service_type=service_type,
                status=AttendanceLog.STATUS_REFUSE,
                reason=reason,
                scanned_by=scanned_by_user_id
            )
            return False, log, student, msg

        # 5. Vérification du jour autorisé par le forfait (plan)
        if not active_sub.plan.is_day_allowed(check_date):
            log = AttendanceService._record_log(
                student_id=student.id,
                timestamp=check_datetime,
                service_type=service_type,
                status=AttendanceLog.STATUS_REFUSE,
                reason=AttendanceLog.REASON_DAY_NOT_ALLOWED,
                scanned_by=scanned_by_user_id
            )
            return False, log, student, f"Accès refusé : Le jour ({check_date.strftime('%A')}) n'est pas inclus dans le forfait '{active_sub.plan.name}'."

        # 6. Vérification du nombre de repas / service (RG-FRQ-02 : 1 passage par service par jour)
        # On recherche un passage AUTORISE pour cet étudiant, ce jour, sur ce même service
        start_of_day = datetime.combine(check_date, time.min)
        end_of_day = datetime.combine(check_date, time.max)

        already_eaten = AttendanceLog.query.filter(
            AttendanceLog.student_id == student.id,
            AttendanceLog.timestamp >= start_of_day,
            AttendanceLog.timestamp <= end_of_day,
            AttendanceLog.service_type == service_type,
            AttendanceLog.status == AttendanceLog.STATUS_AUTORISE
        ).first()

        if already_eaten:
            log = AttendanceService._record_log(
                student_id=student.id,
                timestamp=check_datetime,
                service_type=service_type,
                status=AttendanceLog.STATUS_REFUSE,
                reason=AttendanceLog.REASON_ALREADY_USED,
                scanned_by=scanned_by_user_id
            )
            return False, log, student, f"Accès refusé : Repas ({service_type.lower()}) déjà consommé aujourd'hui à {already_eaten.formatted_time}."

        # 7. Si le plan n'autorise qu'un seul repas par jour et qu'il est déjà venu à l'autre service
        if active_sub.plan.meals_per_day == 1:
            other_eaten = AttendanceLog.query.filter(
                AttendanceLog.student_id == student.id,
                AttendanceLog.timestamp >= start_of_day,
                AttendanceLog.timestamp <= end_of_day,
                AttendanceLog.status == AttendanceLog.STATUS_AUTORISE
            ).first()
            if other_eaten:
                log = AttendanceService._record_log(
                    student_id=student.id,
                    timestamp=check_datetime,
                    service_type=service_type,
                    status=AttendanceLog.STATUS_REFUSE,
                    reason=AttendanceLog.REASON_NOT_ENOUGH_MEALS,
                    scanned_by=scanned_by_user_id
                )
                return False, log, student, f"Accès refusé : Le forfait 1 repas/jour a déjà été utilisé aujourd'hui ({other_eaten.service_type.lower()})."

        # 8. Tout est conforme -> Accès AUTORISÉ !
        log = AttendanceService._record_log(
            student_id=student.id,
            timestamp=check_datetime,
            service_type=service_type,
            status=AttendanceLog.STATUS_AUTORISE,
            reason=None,
            scanned_by=scanned_by_user_id
        )
        return True, log, student, f"Accès autorisé ! Bienvenue {student.first_name}."

    @staticmethod
    def _record_log(student_id, timestamp, service_type, status, reason=None, scanned_by=None):
        """Enregistre un passage dans le journal d'audit."""
        log = AttendanceLog(
            student_id=student_id,
            timestamp=timestamp,
            service_type=service_type,
            status=status,
            refusal_reason=reason,
            scanned_by_user_id=scanned_by
        )
        db.session.add(log)
        db.session.commit()
        return log
