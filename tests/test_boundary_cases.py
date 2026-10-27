import pytest
from datetime import date, timedelta
from app.models.user import User
from app.models.subscription import Subscription
from app.services.auth_service import AuthService
from app.services.student_service import StudentService
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService

# BVA 1 : Montant de paiement 
@pytest.mark.parametrize("montant, doit_echouer", [
    (-0.01, True),
    (0,     True),
    (0.01,  False),
    (60,    False),
])
def test_bva_montant_paiement(app, sample_subscription_en_attente, montant, doit_echouer):
    if doit_echouer:
        with pytest.raises(ValueError):
            PaymentService.record_payment(
                subscription_id=sample_subscription_en_attente.id,
                amount=montant
            )
    else:
        payment = PaymentService.record_payment(
            subscription_id=sample_subscription_en_attente.id,
            amount=montant
        )
        assert payment is not None


# BVA 2 : Complexité mot de passe 
@pytest.mark.parametrize("password, doit_echouer", [
    ("abc1", True),   # 4 caractères.
    ("abcdef1", True),   # 7 caractères. — juste en dessous
    ("abcdefg1", False),  # 8 caractères. — borne valide
    ("abcdefgh1", False),  # 9 caractères.
    ("password", True),   # 8 caractères. sans chiffre
    ("12345678", True),   # 8 caractères. sans lettre
])
def test_bva_complexite_mot_de_passe(app, password, doit_echouer):
    if doit_echouer:
        with pytest.raises(ValueError):
            AuthService.create_user(
                username="test_user",
                email="test@test.fr",
                password=password,
                full_name="Test User",
                role=User.ROLE_AGENT
            )
    else:
        user = AuthService.create_user(
            username="test_user",
            email="test@test.fr",
            password=password,
            full_name="Test User",
            role=User.ROLE_AGENT
        )
        assert user is not None


#  BVA 3 : Format matricule 
@pytest.mark.parametrize("matricule, doit_echouer", [
    ("ETU-99", True), # trop court
    ("ETU-9999", True), # 4 chiffres — juste en dessous
    ("ETU-99001", False), # 5 chiffres — valide
    ("ETU-990011", True), # 6 chiffres — trop long
    ("99001",True), # sans préfixe
])
def test_bva_format_matricule(app, matricule, doit_echouer):
    if doit_echouer:
        with pytest.raises(ValueError):
            StudentService.register_student(
                matricule=matricule,
                first_name="Jean",
                last_name="Dupont",
                email=f"test{matricule.replace('-','')}@test.fr",
                class_name="Terminale"
            )
    else:
        student = StudentService.register_student(
            matricule=matricule,
            first_name="Jean",
            last_name="Dupont",
            email=f"test{matricule.replace('-','')}@test.fr",
            class_name="Terminale"
        )
        assert student is not None


#  BVA 4 : Dates d'abonnement (RG-ABO-01) 
@pytest.mark.parametrize("delta_end, doit_echouer", [
    (-1, True),   # end < start → invalide
    (0, False),  # end = start → valide
    (1, False),  # end = start + 1j → valide
    (30, False),  # durée standard → valide
])
def test_bva_dates_abonnement(app, sample_student, sample_plan, delta_end, doit_echouer):
    start = date.today()
    end = start + timedelta(days=delta_end)
    if doit_echouer:
        with pytest.raises(ValueError):
            SubscriptionService.create_subscription(
                student_id=sample_student.id,
                plan_id=sample_plan.id,
                start_date=start,
                end_date=end
            )
    else:
        sub = SubscriptionService.create_subscription(
            student_id=sample_student.id,
            plan_id=sample_plan.id,
            start_date=start,
            end_date=end
        )
        assert sub is not None