import click
from datetime import date, timedelta, datetime
from app import db
from app.models.user import User
from app.models.student import Student
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.attendance import AttendanceLog
from app.services.auth_service import AuthService

def register_commands(app):
    """Enregistre les commandes CLI personnalisées de Flask."""

    @app.cli.command('init-db')
    def init_db():
        """Initialise la base de données (crée toutes les tables)."""
        db.create_all()
        click.echo("Base de données initialisée avec succès.")

    @app.cli.command('seed')
    def seed_db():
        """Réinitialise et peuple la base de données avec des jeux de données d'essai pour le cours."""
        click.echo("Suppression des anciennes données...")
        db.drop_all()
        db.create_all()

        click.echo("Création des utilisateurs système...")
        # 1. Utilisateurs
        admin = AuthService.create_user(
            username="admin",
            email="admin@cantine-ecole.fr",
            password="Admin123!",
            full_name="Directeur Administrateur",
            role=User.ROLE_ADMIN
        )

        gestionnaire = AuthService.create_user(
            username="gestionnaire",
            email="gestion@cantine-ecole.fr",
            password="Gest123!",
            full_name="Marie Gestionnaire",
            role=User.ROLE_GESTIONNAIRE
        )

        agent = AuthService.create_user(
            username="agent",
            email="agent@cantine-ecole.fr",
            password="Agent123!",
            full_name="Paul Agent Pointage",
            role=User.ROLE_AGENT
        )

        click.echo("Création des formules d'abonnement...")
        # 2. Formules d'abonnement
        # Lundi=0, Mardi=1, Mercredi=2, Jeudi=3, Vendredi=4, Samedi=5, Dimanche=6
        plan_dp4 = SubscriptionPlan(
            code="DP_4J",
            name="Demi-Pension 4 Jours (Lun, Mar, Jeu, Ven)",
            description="Accès au déjeuner les lundis, mardis, jeudis et vendredis.",
            price_monthly=52.00,
            days_allowed="0,1,3,4",
            meals_per_day=1,
            is_active=True
        )

        plan_pt5 = SubscriptionPlan(
            code="PT_5J",
            name="Plein Temps 5 Jours (Lun - Ven)",
            description="Accès au déjeuner tous les midis du lundi au vendredi.",
            price_monthly=65.00,
            days_allowed="0,1,2,3,4",
            meals_per_day=1,
            is_active=True
        )

        plan_pc7 = SubscriptionPlan(
            code="PC_7J",
            name="Pension Complète 7 Jours (Midi & Soir)",
            description="Accès aux déjeuners et dîners 7 jours sur 7 (internat).",
            price_monthly=140.00,
            days_allowed="0,1,2,3,4,5,6",
            meals_per_day=2,
            is_active=True
        )

        db.session.add_all([plan_dp4, plan_pt5, plan_pc7])
        db.session.commit()

        click.echo("Création des profils étudiants d'essai...")
        # 3. Étudiants aux profils variés pour tests
        today = date.today()

        # Profil 1 : Étudiant à jour avec abonnement 5j actif et payé
        s1 = Student(
            matricule="ETU-10001",
            first_name="Lucas",
            last_name="Martin",
            email="lucas.martin@ecole.fr",
            class_name="Terminale S1",
            phone="0601020304",
            is_active=True
        )

        # Profil 2 : Étudiant avec abonnement actif mais forfait 4j (pour tester jour non autorisé le mercredi)
        s2 = Student(
            matricule="ETU-10002",
            first_name="Camille",
            last_name="Dubois",
            email="camille.dubois@ecole.fr",
            class_name="1ère ES",
            phone="0611223344",
            is_active=True
        )

        # Profil 3 : Étudiant avec abonnement expiré
        s3 = Student(
            matricule="ETU-10003",
            first_name="Youssef",
            last_name="Benali",
            email="youssef.benali@ecole.fr",
            class_name="Terminale L",
            phone="0622334455",
            is_active=True
        )

        # Profil 4 : Étudiant avec abonnement suspendu pour impayé
        s4 = Student(
            matricule="ETU-10004",
            first_name="Emma",
            last_name="Leroy",
            email="emma.leroy@ecole.fr",
            class_name="Seconde 3",
            phone="0633445566",
            is_active=True
        )

        # Profil 5 : Étudiant inscrit mais SANS aucun abonnement
        s5 = Student(
            matricule="ETU-10005",
            first_name="Thomas",
            last_name="Moreau",
            email="thomas.moreau@ecole.fr",
            class_name="Terminale STI",
            phone="0644556677",
            is_active=True
        )

        # Profil 6 : Étudiant inactif (dossier suspendu / parti de l'établissement)
        s6 = Student(
            matricule="ETU-10006",
            first_name="Chloé",
            last_name="Roux",
            email="chloe.roux@ecole.fr",
            class_name="Terminale S2",
            phone="0655667788",
            is_active=False
        )

        db.session.add_all([s1, s2, s3, s4, s5, s6])
        db.session.commit()

        click.echo("Création des abonnements et règlements...")
        # 4. Abonnements associés
        # Sub 1 : En cours (du début de mois à fin de mois) - PAYE
        start_curr = today.replace(day=1)
        end_curr = start_curr + timedelta(days=30)
        sub1 = Subscription(
            student_id=s1.id,
            plan_id=plan_pt5.id,
            start_date=start_curr,
            end_date=end_curr,
            status=Subscription.STATUS_ACTIF,
            auto_renew=True
        )
        db.session.add(sub1)
        db.session.flush()

        # Paiement sub 1
        p1 = Payment(
            subscription_id=sub1.id,
            student_id=s1.id,
            amount=plan_pt5.price_monthly,
            payment_date=start_curr,
            payment_method=Payment.METHOD_CARTE,
            status=Payment.STATUS_PAYE,
            reference=Payment.generate_reference(),
            receipt_number=Payment.generate_receipt_number(),
            notes="Paiement en ligne par carte bancaire"
        )
        db.session.add(p1)

        # Sub 2 : En cours (forfait 4j) - PAYE
        sub2 = Subscription(
            student_id=s2.id,
            plan_id=plan_dp4.id,
            start_date=start_curr,
            end_date=end_curr,
            status=Subscription.STATUS_ACTIF,
            auto_renew=True
        )
        db.session.add(sub2)
        db.session.flush()

        p2 = Payment(
            subscription_id=sub2.id,
            student_id=s2.id,
            amount=plan_dp4.price_monthly,
            payment_date=start_curr,
            payment_method=Payment.METHOD_ESPECES,
            status=Payment.STATUS_PAYE,
            reference=Payment.generate_reference(),
            receipt_number=Payment.generate_receipt_number(),
            notes="Règlement espèces à l'intendance"
        )
        db.session.add(p2)

        # Sub 3 : Expiré le mois dernier
        start_old = start_curr - timedelta(days=35)
        end_old = start_curr - timedelta(days=5)
        sub3 = Subscription(
            student_id=s3.id,
            plan_id=plan_pt5.id,
            start_date=start_old,
            end_date=end_old,
            status=Subscription.STATUS_EXPIRE,
            auto_renew=False
        )
        db.session.add(sub3)

        # Sub 4 : Suspendu pour impayé
        sub4 = Subscription(
            student_id=s4.id,
            plan_id=plan_pt5.id,
            start_date=start_curr,
            end_date=end_curr,
            status=Subscription.STATUS_SUSPENDU,
            auto_renew=True
        )
        db.session.add(sub4)

        # 5. Quelques logs de fréquentation passés
        log1 = AttendanceLog(
            student_id=s1.id,
            timestamp=datetime.now() - timedelta(days=1, hours=2),
            service_type=AttendanceLog.SERVICE_DEJEUNER,
            status=AttendanceLog.STATUS_AUTORISE,
            scanned_by_user_id=agent.id
        )
        db.session.add(log1)

        db.session.commit()
        click.echo("=" * 60)
        click.echo("Données d'essai injectées avec succès !")
        click.echo("Comptes utilisateurs créés :")
        click.echo("  - ADMIN         : admin / Admin123!")
        click.echo("  - GESTIONNAIRE  : gestionnaire / Gest123!")
        click.echo("  - AGENT POINTAGE: agent / Agent123!")
        click.echo("Matricules étudiants types :")
        click.echo("  - ETU-10001 : Lucas Martin (Abonnement Plein Temps ACTIF & PAYE)")
        click.echo("  - ETU-10002 : Camille Dubois (Demi-Pension 4J - Hors Mercredi)")
        click.echo("  - ETU-10003 : Youssef Benali (Abonnement EXPIRE)")
        click.echo("  - ETU-10004 : Emma Leroy (Abonnement SUSPENDU pour impayé)")
        click.echo("  - ETU-10005 : Thomas Moreau (AUCUN abonnement)")
        click.echo("  - ETU-10006 : Chloé Roux (Étudiant INACTIF)")
        click.echo("=" * 60)
