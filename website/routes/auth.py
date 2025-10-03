import jwt
from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response

from config import SECRET_KEY
from website import db
from website.utils import first_setup_only, login_only_if_configured, login_required

auth = Blueprint("auth", __name__)


@auth.route("/first-setup", methods=["GET", "POST"])
@first_setup_only
def first_setup() -> Response | str:
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "")
        username = request.form.get("username", "")
        password = request.form.get("password1", "")
        password2 = request.form.get("password2", "")

        if len(name) < 2:
            flash("Name must be at least 2 characters long", category="danger")
        elif len(email) < 5:
            flash("Please enter a valid email address", category="danger")
        elif len(username) < 2:
            flash("Username must be at least 2 characters long", category="danger")
        elif len(password) < 3:
            flash("Password must be at least 3 characters long", category="danger")
        elif password != password2:
            flash("Passwords do not match", category="danger")
        else:
            response = db.register(
                email=email,
                username=username,
                display_name=name,
                password=password,
                role="superadmin",
            )
            if response.type == "error":
                flash(response.message, category="danger")
            else:
                flash(response.message, category="success")
                return redirect(url_for("auth.login"))
    return render_template("first_setup.html")


@auth.route("/login", methods=["GET", "POST"])
@login_only_if_configured
def login() -> Response | str:
    if request.method == "POST":
        email_or_username = request.form.get("email_or_username", "")
        password = request.form.get("password", "")

        if len(email_or_username) < 2:
            flash("Please enter a valid email or username", category="danger")
        elif len(password) < 3:
            flash("Password must be at least 3 characters long", category="danger")
        else:
            response = db.login(email_or_username=email_or_username, password=password)
            if response.type == "success" and response.data:
                flash(response.message, category="success")
                access_token = jwt.encode(
                    {"user_id": response.data.user.id},
                    SECRET_KEY,
                    algorithm="HS256",
                )
                refresh_token = response.data.refresh_token
                res = make_response(redirect(url_for("views.home")))
                res.set_cookie(
                    "access_token",
                    access_token,
                    httponly=True,
                    samesite="Lax",
                    max_age=7 * 24 * 3600,
                )
                res.set_cookie(
                    "refresh_token",
                    refresh_token,
                    httponly=True,
                    samesite="Lax",
                    max_age=30 * 24 * 3600,
                )
                return res
            else:
                flash(response.message, category="danger")
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout() -> Response:
    response = db.logout()
    if response.type == "error":
        flash(response.message, category="danger")
        return redirect(url_for("views.home"))
    else:
        flash(response.message, category="success")
        res = make_response(redirect(url_for("auth.login")))
        res.delete_cookie("access_token")
        res.delete_cookie("refresh_token")
        return res
