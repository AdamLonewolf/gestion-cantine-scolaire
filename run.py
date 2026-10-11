import os
from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.attendance import AttendanceLog

config_name = os.environ.get('FLASK_CONFIG', 'default')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Injecte les modèles directement dans le shell Flask."""
    return dict(
        db=db,
        User=User,
        Student=Student,
        SubscriptionPlan=SubscriptionPlan,
        Subscription=Subscription,
        Payment=Payment,
        AttendanceLog=AttendanceLog
    )

if __name__ == '__main__':
    # Initialisation automatique des tables au premier démarrage si la base n'existe pas
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)
