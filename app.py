from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

from config import config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(config)
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    mail.init_app(flask_app)

    from routes.auth import auth
    from routes.public import public
    from routes.student import student_routes
    from routes.teacher import teacher_routes
    from routes.cashier import cashier_routes
    flask_app.register_blueprint(auth, url_prefix='/')
    flask_app.register_blueprint(public, url_prefix='/')
    flask_app.register_blueprint(student_routes, url_prefix='/student')
    flask_app.register_blueprint(teacher_routes, url_prefix='/teacher')
    flask_app.register_blueprint(cashier_routes, url_prefix='/cashier')

    login = LoginManager()
    login.login_view = 'auth.login'
    login.init_app(flask_app)

    from models import Student, Staff
    @login.user_loader
    def load_user(user_id):
        try:
            user_type, real_id = user_id.split(":")
        except ValueError:
            return None
        if user_type == "student":
            return Student.query.get(int(real_id))
        return Staff.query.get(int(real_id))
    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
