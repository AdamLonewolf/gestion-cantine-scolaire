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
            matricule="ETU-99002",  
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
def test_student_inactive_subscription_refusee(app, sample_student_inactif, sample_plan):
    with pytest.raises(ValueError):
        SubscriptionService.create_subscription(
            student_id=sample_student_inactif.id,
            plan_id=sample_plan.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)  
        )

"""Cas 6 : Mise à jour des informations d'un étudiant existant"""
def test_update_student(app, sample_student):
    updated = StudentService.update_student(
        student_id=sample_student.id,
        first_name="Jean-Luc",
        last_name="Dupont",
        email="jeanluc.dupont@test.fr",
        class_name="Terminale B",
        is_active=True
    )
    assert updated.first_name == "Jean-Luc"
    assert updated.email == "jeanluc.dupont@test.fr"

"""Cas 7 : Mise à jour d'un étudiant inexistant — lève une ValueError"""
def test_update_student_inexistant(app):
    with pytest.raises(ValueError):
        StudentService.update_student(
            student_id=99999,
            first_name="Jean",
            last_name="Dupont",
            email="jean@test.fr",
            class_name="Terminale"
        )

"""Cas 8 : Bascule du statut actif/inactif d'un étudiant"""
def test_toggle_status_student(app, sample_student):
    statut_initial = sample_student.is_active
    updated = StudentService.toggle_status(sample_student.id)
    assert updated.is_active != statut_initial

"""Cas 9 : Bascule du statut d'un étudiant inexistant — lève une ValueError"""
def test_toggle_status_student_inexistant(app):
    with pytest.raises(ValueError):
        StudentService.toggle_status(99999)


"""Cas 10 : Email vide dans register_student — lève une ValueError"""
def test_register_email_vide(app):
    with pytest.raises(ValueError):
        StudentService.register_student(
            matricule="ETU-88002",
            first_name="Jean",
            last_name="Dupont",
            email="",
            class_name="Terminale"
        )

"""Cas 11 : Email format invalide — lève une ValueError"""
def test_register_email_invalide(app):
    with pytest.raises(ValueError):
        StudentService.register_student(
            matricule="ETU-88003",
            first_name="Jean",
            last_name="Dupont",
            email="pasunemail",
            class_name="Terminale"
        )

"""Cas 12 : Classe vide — lève une ValueError"""
def test_register_classe_vide(app):
    with pytest.raises(ValueError):
        StudentService.register_student(
            matricule="ETU-88004",
            first_name="Jean",
            last_name="Dupont",
            email="jean88004@test.fr",
            class_name=""
        )

"""Cas 13 : update_student avec email format invalide — lève une ValueError"""
def test_update_student_email_invalide(app, sample_student):
    with pytest.raises(ValueError):
        StudentService.update_student(
            student_id=sample_student.id,
            first_name="Jean",
            last_name="Dupont",
            email="pasunemail",
            class_name="Terminale"
        )

"""Cas 14 : update_student avec email en doublon — lève une ValueError"""
def test_update_student_email_doublon(app, sample_student, sample_student_inactif):
    with pytest.raises(ValueError):
        StudentService.update_student(
            student_id=sample_student.id,
            first_name="Jean",
            last_name="Dupont",
            email="marie.dupont@test.fr",  # email de sample_student_inactif
            class_name="Terminale"
        )

"""Cas 15 : matricule valide mais prénom vide"""
def test_register_student_prenom_vide(app):
    with pytest.raises(ValueError, match="prénom et le nom"):
        StudentService.register_student(
            matricule="ETU-77001",
            first_name="",        
            last_name="Dupont",
            email="test77001@test.fr",
            class_name="Terminale"
        )