from datetime import datetime, date
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.attendance import AttendanceLog
from app.models.student import Student
from app.services.attendance_service import AttendanceService
from app.routes.decorators import role_required
from app.models.user import User

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE, User.ROLE_AGENT)
def terminal():
    """Borne interactive de pointage et contrôle d'accès au réfectoire."""
    check_result = None
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    current_service = AttendanceService.determine_service_type(datetime.now())

    if request.method == 'POST':
        matricule = request.form.get('matricule', '').strip().upper()
        service_type = request.form.get('service_type') or current_service

        is_auth, log, student, msg = AttendanceService.process_check_in(
            matricule=matricule,
            scanned_by_user_id=current_user.id,
            service_type=service_type
        )

        check_result = {
            'is_authorized': is_auth,
            'student': student,
            'message': msg,
            'log': log,
            'matricule': matricule
        }

    # Derniers passages du jour pour affichage direct sous la borne
    today_logs = AttendanceLog.query.filter(
        AttendanceLog.timestamp >= start_of_day,
        AttendanceLog.timestamp <= end_of_day
    ).order_by(AttendanceLog.timestamp.desc()).limit(10).all()

    # Statistiques du jour
    auth_count = AttendanceLog.query.filter(
        AttendanceLog.timestamp >= start_of_day,
        AttendanceLog.timestamp <= end_of_day,
        AttendanceLog.status == AttendanceLog.STATUS_AUTORISE
    ).count()

    refuse_count = AttendanceLog.query.filter(
        AttendanceLog.timestamp >= start_of_day,
        AttendanceLog.timestamp <= end_of_day,
        AttendanceLog.status == AttendanceLog.STATUS_REFUSE
    ).count()

    return render_template(
        'attendance/terminal.html',
        check_result=check_result,
        today_logs=today_logs,
        current_service=current_service,
        services=AttendanceLog.SERVICES,
        auth_count=auth_count,
        refuse_count=refuse_count
    )

@attendance_bp.route('/api/scan', methods=['POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE, User.ROLE_AGENT)
def api_scan():
    """API JSON pour scan de code-barres / badgeuse ou tests automatisés."""
    data = request.get_json() or {}
    matricule = data.get('matricule', '').strip().upper()
    service_type = data.get('service_type')

    is_auth, log, student, msg = AttendanceService.process_check_in(
        matricule=matricule,
        scanned_by_user_id=current_user.id,
        service_type=service_type
    )

    return jsonify({
        'authorized': is_auth,
        'matricule': matricule,
        'student_name': student.full_name if student else None,
        'class_name': student.class_name if student else None,
        'message': msg,
        'status': log.status if log else 'REFUSE',
        'refusal_reason': log.refusal_reason if log else 'NOT_FOUND',
        'timestamp': log.timestamp.isoformat() if log else datetime.utcnow().isoformat()
    }), (200 if is_auth else 400)

@attendance_bp.route('/history')
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE, User.ROLE_AGENT)
def history():
    """Journal complet des passages avec filtres."""
    status_filter = request.args.get('status', '').strip()
    query = AttendanceLog.query.join(Student)

    if status_filter in AttendanceLog.STATUSES:
        query = query.filter(AttendanceLog.status == status_filter)

    logs = query.order_by(AttendanceLog.timestamp.desc()).limit(100).all()
    return render_template('attendance/history.html', logs=logs, status_filter=status_filter)
