import pytest
from datetime import date, timedelta
from app.services.student_service import StudentService
from app.models.student import Student
from datetime import date, timedelta
from app.services.subscription_service import SubscriptionService
from app.models.subscription import Subscription


#Tests Etudiants

"""
    CAS 1 : Un étudiant est sur le point d'être enregistré avec un matricule
    au format invalide.
"""
def test_student_matricule_invalide(app):
    with pytest.raises(ValueError):
         StudentService.register_student(
                matricule="ETU-99",
                first_name="Adam",
                last_name="Coulibaly",
                email="adam.coul@test.fr",
                class_name="Terminale Test",
            )


"""
    CAS 2 : Un étudiant est sur le point d'être enregistré avec un matricule
    déjà existant (doublon)
"""
def test_student_matricule_doublon(sample_student, app) :
    with pytest.raises(ValueError):
        StudentService.register_student(
            matricule="ETU-99001",
            first_name="Adam",
            last_name="Coulibaly",
            email="adam.coul@test.fr",
            class_name="Terminale Test",
        )


"""
    CAS 3 : Un étudiant est sur le point d'être enregistré avec un email
    déjà existant (doublon)
"""
def test_student_email_doublon(sample_student, app) :
    with pytest.raises(ValueError):
        StudentService.register_student(
            matricule="ETU-99001",
            first_name="Adam",
            last_name="Coulibaly",
            email="jean.dupont@test.fr",
            class_name="Terminale Test",
        )
        

"""
    CAS 4 : Enregistrement d'un étudiant avec des champs vides
"""
def test_student_registrer_empty_fields(sample_student, app) :
    with pytest.raises(ValueError):
        StudentService.register_student(
            matricule="",
            first_name="",
            last_name="",
            email="",
            class_name="",
        )


"""
    CAS 5 : Un Étudiant avec un compte inactif ne peut pas souscrire à un abonnement.
"""
def test_student_inactive_subscription_refusee(app, sample_student_inactif, sample_plan, sample_student):
    start = date.today()
    end = date.today() - timedelta(days=5)
    with pytest.raises(ValueError):
        SubscriptionService.create_subscription(
            student_id=sample_student_inactif.id,
            plan_id=sample_plan.id,
            start_date=start,
            end_date=end
        )