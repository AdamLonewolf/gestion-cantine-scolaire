import pytest
from datetime import date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.services.auth_service import AuthService

@pytest.fixture
def app():
    """Crée une instance de l'application Flask configurée pour les tests."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Client de test HTTP Flask."""
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Utilisateur administrateur de test."""
    return AuthService.create_user(
        username="admin_test",
        email="admin_test@test.fr",
        password="Password123!",
        full_name="Admin Testeur",
        role=User.ROLE_ADMIN
    )

@pytest.fixture
def gestionnaire_user(app):
    """Utilisateur gestionnaire de test."""
    return AuthService.create_user(
        username="gest_test",
        email="gest_test@test.fr",
        password="Password123!",
        full_name="Gestionnaire Testeur",
        role=User.ROLE_GESTIONNAIRE
    )

@pytest.fixture
def agent_user(app):
    """Utilisateur agent de pointage de test."""
    return AuthService.create_user(
        username="agent_test",
        email="agent_test@test.fr",
        password="Password123!",
        full_name="Agent Testeur",
        role=User.ROLE_AGENT
    )

@pytest.fixture
def auth_admin_client(client, admin_user):
    """Client authentifié avec les droits Administrateur."""
    client.post('/login', data={'username': 'admin_test', 'password': 'Password123!'})
    return client

@pytest.fixture
def auth_gestionnaire_client(client, gestionnaire_user):
    """Client authentifié avec les droits Gestionnaire."""
    client.post('/login', data={'username': 'gest_test', 'password': 'Password123!'})
    return client

@pytest.fixture
def auth_agent_client(client, agent_user):
    """Client authentifié avec les droits Agent Pointage."""
    client.post('/login', data={'username': 'agent_test', 'password': 'Password123!'})
    return client

@pytest.fixture
def sample_plan(app):
    """Formule d'abonnement 5 jours (Lundi à Vendredi)."""
    plan = SubscriptionPlan(
        code="TEST_5J",
        name="Forfait 5 Jours Semaine",
        price_monthly=60.0,
        days_allowed="0,1,2,3,4",
        meals_per_day=1,
        is_active=True
    )
    db.session.add(plan)
    db.session.commit()
    return plan

@pytest.fixture
def sample_plan_4j(app):
    """Formule d'abonnement 4 jours (Lundi, Mardi, Jeudi, Vendredi - SANS Mercredi)."""
    plan = SubscriptionPlan(
        code="TEST_4J",
        name="Forfait 4 Jours (Sans Mercredi)",
        price_monthly=48.0,
        days_allowed="0,1,3,4",
        meals_per_day=1,
        is_active=True
    )
    db.session.add(plan)
    db.session.commit()
    return plan

@pytest.fixture
def sample_student(app):
    """Étudiant de test actif."""
    student = Student(
        matricule="ETU-99001",
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@test.fr",
        class_name="Terminale Test",
        is_active=True
    )
    db.session.add(student)
    db.session.commit()
    return student
