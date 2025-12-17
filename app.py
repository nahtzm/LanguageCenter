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
    flask_app.register_blueprint(auth, url_prefix='/')
    flask_app.register_blueprint(public, url_prefix='/')

    login = LoginManager()
    login.login_view = 'auth.login'
    login.init_app(flask_app)

    # @login.user_loader
    # def load_user(user_id):
    #     return db.session.get(User, int(user_id))
    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run()
