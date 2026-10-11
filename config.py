import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuration de base."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cantine-secret-key-pour-test-et-val-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Désactivé par défaut pour simplifier les tests des étudiants

    # Horaires de service pour le pointage
    LUNCH_START_HOUR = 11  # 11h30
    LUNCH_START_MIN = 30
    LUNCH_END_HOUR = 14    # 14h00
    LUNCH_END_MIN = 0

    DINNER_START_HOUR = 18 # 18h30
    DINNER_START_MIN = 30
    DINNER_END_HOUR = 20   # 20h30
    DINNER_END_MIN = 30

class DevelopmentConfig(Config):
    """Configuration de développement."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'cantine_dev.db')
    )

class TestingConfig(Config):
    """Configuration pour les tests automatisés (Pytest)."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuration de production."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'cantine.db')
    )

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
