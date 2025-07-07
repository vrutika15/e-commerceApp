# app/__init__.py
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from app.extensions import db, bcrypt, login_manager, mail
from app.routes import register_blueprints
from flask_wtf.csrf import CSRFProtect

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf = CSRFProtect(app)

    #register_blueprint
    register_blueprints(app)


    from app.models import User 
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
