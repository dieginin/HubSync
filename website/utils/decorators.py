from functools import wraps

from flask import g, make_response, redirect, request, url_for
from werkzeug import Response


def login_required(f):
    from website import db

    def is_token_expiring_soon(expires_at: int, threshold_minutes: int = 5) -> bool:
        import time

        current_time = int(time.time())
        threshold_seconds = threshold_minutes * 60
        time_until_expiry = expires_at - current_time
        return time_until_expiry <= threshold_seconds and time_until_expiry > 0

    def set_user(user_id: str) -> None:
        from website.models import User

        user_data = db.get_user_by_eq("id", user_id)
        if user_data:
            g.user = User(
                id=user_data[0]["id"],
                email=user_data[0]["email"],
                username=user_data[0]["username"],
                display_name=user_data[0]["display_name"],
                role=user_data[0]["role"],
            )

    def set_new_cookies(
        response: Response, access_token: str, refresh_token: str
    ) -> None:
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            samesite="Lax",
            max_age=7 * 24 * 3600,  # 7 días
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            samesite="Lax",
            max_age=30 * 24 * 3600,  # 30 días
        )

    def clear_cookies_and_redirect() -> Response:
        response = make_response(redirect(url_for("auth.login")))
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response | str:
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if not access_token and not refresh_token:
            return clear_cookies_and_redirect()

        payload = None
        if access_token and refresh_token:
            try:
                if db.set_session_from_tokens(access_token, refresh_token):
                    user_response = db.auth.get_user()
                    if user_response and user_response.user:
                        payload = {"user_id": user_response.user.id}

                        try:
                            current_session = db.auth.get_session()
                            if (
                                current_session
                                and hasattr(current_session, "expires_at")
                                and current_session.expires_at is not None
                            ):
                                if is_token_expiring_soon(
                                    current_session.expires_at, threshold_minutes=5
                                ):
                                    refresh_response = db.refresh_session(refresh_token)

                                    if (
                                        refresh_response.type == "success"
                                        and refresh_response.data
                                    ):
                                        new_access_token = (
                                            refresh_response.data.access_token
                                        )
                                        new_refresh_token = (
                                            refresh_response.data.refresh_token
                                        )

                                        db.set_session_from_tokens(
                                            new_access_token, new_refresh_token
                                        )

                                        response = make_response(f(*args, **kwargs))
                                        set_new_cookies(
                                            response,
                                            new_access_token,
                                            new_refresh_token,
                                        )

                                        set_user(payload["user_id"])
                                        return response
                        except:
                            ...
            except:
                payload = None

        if not payload and refresh_token:
            refresh_response = db.refresh_session(refresh_token)
            if refresh_response.type == "success" and refresh_response.data:
                new_access_token = refresh_response.data.access_token
                new_refresh_token = refresh_response.data.refresh_token

                response = make_response(redirect(request.url))
                set_new_cookies(response, new_access_token, new_refresh_token)

                try:
                    db.set_session_from_tokens(new_access_token, new_refresh_token)
                except Exception as e:
                    print(f"Warning: Could not set Supabase session after refresh: {e}")

                return response
            else:
                return clear_cookies_and_redirect()

        if payload and "user_id" in payload:
            set_user(payload["user_id"])
            return f(*args, **kwargs)
        else:
            return clear_cookies_and_redirect()

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
        if request.cookies.get("access_token"):
            return redirect(url_for("views.home"))
        return f(*args, **kwargs)

    return decorated_function
