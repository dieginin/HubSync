from flask import Flask, Response, send_from_directory

from config import SECRET_KEY
from website.services import DatabaseManager

db = DatabaseManager()


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    from .routes import auth, views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app
