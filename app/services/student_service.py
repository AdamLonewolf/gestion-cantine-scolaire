import re
from app import db
from app.models.student import Student

class StudentService:
    """Service gérant l'inscription et le cycle de vie des étudiants."""

    MATRICULE_REGEX = r'^ETU-\d{5}$'

    @staticmethod
    def validate_matricule(matricule):
        """
        RG-ETU-01 : Le matricule étudiant est obligatoire, unique et suit le format ETU-XXXXX (5 chiffres).
        """
        if not matricule:
            return False, "Le matricule est obligatoire."
        matricule = matricule.strip().upper()
        if not re.match(StudentService.MATRICULE_REGEX, matricule):
            return False, "Le matricule doit respecter le format 'ETU-XXXXX' (5 chiffres, ex: ETU-10042)."
        return True, ""

    @staticmethod
    def validate_email(email):
        """RG-ETU-02 : L'adresse email doit être valide et unique."""
        if not email:
            return False, "L'adresse email est obligatoire."
        email = email.strip().lower()
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return False, "Format d'adresse email invalide."
        return True, ""

    @staticmethod
    def register_student(matricule, first_name, last_name, email, class_name, phone=None):
        """Enregistre un nouvel étudiant avec contrôles des règles métier."""
        matricule = (matricule or "").strip().upper()
        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        email = (email or "").strip().lower()
        class_name = (class_name or "").strip()
        phone = (phone or "").strip() or None

        # Validation matricule
        m_valid, m_err = StudentService.validate_matricule(matricule)
        if not m_valid:
            raise ValueError(m_err)

        # Unicité matricule
        if Student.query.filter_by(matricule=matricule).first():
            raise ValueError(f"Le matricule '{matricule}' est déjà attribué à un autre étudiant.")

        # Validation nom & prénom
        if not first_name or not last_name:
            raise ValueError("Le prénom et le nom de l'étudiant sont obligatoires.")

        # Validation email
        e_valid, e_err = StudentService.validate_email(email)
        if not e_valid:
            raise ValueError(e_err)

        # Unicité email
        if Student.query.filter_by(email=email).first():
            raise ValueError(f"L'adresse email '{email}' est déjà utilisée par un autre étudiant.")

        # Validation classe
        if not class_name:
            raise ValueError("La classe / promotion de l'étudiant est obligatoire.")

        student = Student(
            matricule=matricule,
            first_name=first_name,
            last_name=last_name,
            email=email,
            class_name=class_name,
            phone=phone,
            is_active=True
        )
        db.session.add(student)
        db.session.commit()
        return student

    @staticmethod
    def update_student(student_id, first_name, last_name, email, class_name, phone=None, is_active=True):
        """Met à jour les informations d'un étudiant."""
        student = db.session.get(Student, student_id)
        if not student:
            raise ValueError("Étudiant introuvable.")

        email = (email or "").strip().lower()
        e_valid, e_err = StudentService.validate_email(email)
        if not e_valid:
            raise ValueError(e_err)

        existing = Student.query.filter(Student.email == email, Student.id != student_id).first()
        if existing:
            raise ValueError(f"L'adresse email '{email}' est déjà utilisée par un autre étudiant.")

        student.first_name = (first_name or "").strip()
        student.last_name = (last_name or "").strip()
        student.email = email
        student.class_name = (class_name or "").strip()
        student.phone = (phone or "").strip() or None
        student.is_active = bool(is_active)

        db.session.commit()
        return student

    @staticmethod
    def toggle_status(student_id):
        """Bascule le statut actif/inactif d'un étudiant."""
        student = db.session.get(Student, student_id)
        if not student:
            raise ValueError("Étudiant introuvable.")
        student.is_active = not student.is_active
        db.session.commit()
        return student
