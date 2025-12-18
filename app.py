from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(config)
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    from routes.auth import auth
    from routes.public import public
    from routes.student import student_routes
    flask_app.register_blueprint(auth, url_prefix='/')
    flask_app.register_blueprint(public, url_prefix='/')
    flask_app.register_blueprint(student_routes, url_prefix='/student')

    login = LoginManager()
    login.login_view = 'auth.login'
    login.init_app(flask_app)

    from models import Student, Staff
    @login.user_loader
    def load_user(user_id):
        student = Student.query.get(user_id)
        if student:
            return student
        staff = Staff.query.get(user_id)
        if staff:
            return staff
        return None
    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
