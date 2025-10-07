from functools import wraps

from flask import redirect, url_for
from flask_login import current_user
from werkzeug import Response


def first_setup_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response | str:
        from website import db_manager

        if db_manager.has_users():
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def login_only_if_configured(f):
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response | str:
        from website import db_manager

        if not db_manager.has_users():
            return redirect(url_for("auth.first_setup"))
        if current_user.is_authenticated:
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)

    return decorated_function
