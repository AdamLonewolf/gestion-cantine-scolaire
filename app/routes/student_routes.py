from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.student import Student
from app.models.plan import SubscriptionPlan
from app.services.student_service import StudentService
from app.routes.decorators import role_required
from app.models.user import User

student_bp = Blueprint('students', __name__, url_prefix='/students')

@student_bp.route('/')
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def list_students():
    """Liste des étudiants avec recherche par mot-clé."""
    search = request.args.get('search', '').strip()
    query = Student.query

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Student.matricule.ilike(search_filter)) |
            (Student.first_name.ilike(search_filter)) |
            (Student.last_name.ilike(search_filter)) |
            (Student.class_name.ilike(search_filter)) |
            (Student.email.ilike(search_filter))
        )

    students = query.order_by(Student.matricule.asc()).all()
    return render_template('students/list.html', students=students, search=search)

@student_bp.route('/new', methods=['GET', 'POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def new_student():
    """Inscription d'un nouvel étudiant."""
    if request.method == 'POST':
        matricule = request.form.get('matricule')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        class_name = request.form.get('class_name')
        phone = request.form.get('phone')

        try:
            student = StudentService.register_student(
                matricule=matricule,
                first_name=first_name,
                last_name=last_name,
                email=email,
                class_name=class_name,
                phone=phone
            )
            flash(f"Étudiant {student.full_name} ({student.matricule}) inscrit avec succès.", "success")
            return redirect(url_for('students.student_detail', student_id=student.id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('students/form.html', student=None)

@student_bp.route('/<int:student_id>')
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE, User.ROLE_AGENT)
def student_detail(student_id):
    """Fiche détaillée d'un étudiant avec son historique complet."""
    student = db.session.get(Student, student_id)
    if not student:
        flash("Étudiant introuvable.", "danger")
        return redirect(url_for('students.list_students'))

    current_sub = student.get_active_subscription()
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    subscriptions = student.subscriptions.order_by(db.desc('start_date')).all()
    payments = student.payments.order_by(db.desc('created_at')).limit(10).all()
    attendances = student.attendances.order_by(db.desc('timestamp')).limit(15).all()

    return render_template(
        'students/detail.html',
        student=student,
        current_sub=current_sub,
        plans=plans,
        subscriptions=subscriptions,
        payments=payments,
        attendances=attendances
    )

@student_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def edit_student(student_id):
    """Modification d'un étudiant."""
    student = db.session.get(Student, student_id)
    if not student:
        flash("Étudiant introuvable.", "danger")
        return redirect(url_for('students.list_students'))

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        class_name = request.form.get('class_name')
        phone = request.form.get('phone')
        is_active = bool(request.form.get('is_active'))

        try:
            StudentService.update_student(
                student_id=student.id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                class_name=class_name,
                phone=phone,
                is_active=is_active
            )
            flash(f"Informations de {student.full_name} mises à jour.", "success")
            return redirect(url_for('students.student_detail', student_id=student.id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('students/form.html', student=student)

@student_bp.route('/<int:student_id>/toggle-status', methods=['POST'])
@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GESTIONNAIRE)
def toggle_status(student_id):
    """Bascule actif / inactif d'un étudiant."""
    try:
        student = StudentService.toggle_status(student_id)
        stat = "activé" if student.is_active else "désactivé"
        flash(f"L'étudiant {student.full_name} a été {stat}.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for('students.student_detail', student_id=student_id))
