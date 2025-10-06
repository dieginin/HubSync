from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from .config import DB_NAME, SECRET_KEY

db = SQLAlchemy()

from .models import User


def has_users_in_db() -> bool:
    return db.session.query(User).first() is not None


def _create_database(app: Flask) -> None:
    with app.app_context():
        db.create_all()


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # type: ignore
    login_manager.login_message = ""
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return User.query.get(int(user_id))

    from .routes import auth, main

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(main, url_prefix="/")

    _create_database(app)

    return app
