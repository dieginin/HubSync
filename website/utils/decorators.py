from functools import wraps

import jwt
from flask import g, make_response, redirect, request, url_for
from werkzeug import Response

from config import SECRET_KEY


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response | str:
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if not access_token and not refresh_token:
            return redirect(url_for("auth.login"))

        payload = None
        if access_token:
            try:
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                payload = None
            except:
                return redirect(url_for("auth.login"))
        if not payload and refresh_token:
            from website import db

            resp = db.refresh_session(refresh_token)
            if resp.type == "success" and resp.data:
                new_access_token = jwt.encode(
                    {"access_token": resp.data.access_token},
                    SECRET_KEY,
                    algorithm="HS256",
                )
                new_refresh_token = resp.data.refresh_token
                response = make_response()
                response.set_cookie(
                    "access_token",
                    new_access_token,
                    httponly=True,
                    samesite="Lax",
                    max_age=7 * 24 * 3600,
                )
                response.set_cookie(
                    "refresh_token",
                    new_refresh_token,
                    httponly=True,
                    samesite="Lax",
                    max_age=30 * 24 * 3600,
                )
                g.user = resp.message
                return response
            else:
                return redirect(url_for("auth.login"))
        g.user = payload
        return f(*args, **kwargs)

    return decorated_function


def first_setup_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response | str:
        from website import db

        if db.users_exist:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def login_only_if_configured(f):
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response | str:
        from website import db

        if not db.users_exist:
            return redirect(url_for("auth.first_setup"))
        return f(*args, **kwargs)

    return decorated_function
