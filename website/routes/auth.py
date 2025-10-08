import re

from flask import Blueprint as _Blueprint
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug import Response
from werkzeug.security import check_password_hash

from website import db_manager
from website.config import MIN_LENGTHS
from website.utils import first_setup_only, login_only_if_configured
from website.utils import send_password_reset_email as password_reset_email

auth = _Blueprint("auth", __name__)

is_email = lambda x: bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", x))


@auth.route("/first_setup", methods=["GET", "POST"])
@first_setup_only
def first_setup() -> Response | str:
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "")
        username = request.form.get("username", "")
        password = request.form.get("password1", "")
        password2 = request.form.get("password2", "")

        email_exists = db_manager.get_user_by_email(email) is not None
        user_exists = db_manager.get_user_by_username(username) is not None

        if email_exists:
            flash("Email already exists", category="danger")
        elif user_exists:
            flash("Username already exists", category="danger")
        elif len(name) < MIN_LENGTHS["name"]:
            flash(
                f"Name must be at least {MIN_LENGTHS['name']} characters long",
                category="danger",
            )
        elif len(email) < MIN_LENGTHS["email"]:
            flash(f"Please enter a valid email address", category="danger")
        elif len(username) < MIN_LENGTHS["username"]:
            flash(
                f"Username must be at least {MIN_LENGTHS['username']} characters long",
                category="danger",
            )
        elif len(password) < MIN_LENGTHS["password"]:
            flash(
                f"Password must be at least {MIN_LENGTHS['password']} characters long",
                category="danger",
            )
        elif password != password2:
            flash("Passwords don't match", category="danger")
        else:
            new_user = db_manager.create_user(
                display_name=name,
                email=email,
                username=username,
                role="superadmin",
                password=password,
            )
            login_user(new_user, remember=True)
            flash("Registration successful", category="success")
            return redirect(url_for("main.home"))
    return render_template("first_setup.html")


@auth.route("/login", methods=["GET", "POST"])
@login_only_if_configured
def login() -> Response | str:
    if request.method == "POST":
        email_or_username = request.form.get("email_or_username", "")
        password = request.form.get("password", "")

        if is_email(email_or_username):
            user = db_manager.get_user_by_email(email_or_username)
        else:
            user = db_manager.get_user_by_username(email_or_username)

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Login successful", category="success")
                return redirect(url_for("main.home"))
            else:
                flash("Incorrect password, try again", category="danger")
        else:
            if is_email(email_or_username):
                flash("Email does not exist", category="danger")
            else:
                flash("Username does not exist", category="danger")
    return render_template("login.html")


@auth.route("/forgot_password", methods=["GET", "POST"])
@login_only_if_configured
def forgot_password() -> Response | str:
    if request.method == "POST":
        email = request.form.get("email", "")
        email_exists = db_manager.get_user_by_email(email) is not None

        if email_exists:
            password_reset_email(email)

        flash(
            "If this email is registered, a password reset link has been sent.",
            category="info",
        )
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
@login_only_if_configured
def reset_password(token) -> Response | str:
    email, reset_token = db_manager.verify_reset_password_token(token)
    if not email:
        flash("The link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form.get("password1", "")
        new_password2 = request.form.get("password2", "")
        if len(new_password) < MIN_LENGTHS["password"]:
            flash(
                f"Password must be at least {MIN_LENGTHS['password']} characters long",
                category="danger",
            )
        elif new_password != new_password2:
            flash("Passwords don't match", category="danger")
        else:
            user = db_manager.get_user_by_email(email)
            if user and reset_token:
                reset_token.mark_as_used()
                db_manager.change_password(user.password, new_password, email)
                flash("Your password has been updated.", "success")
                return redirect(url_for("auth.login"))

    return render_template("reset_password.html")


@auth.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    flash("Logout successful", category="success")
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
    return redirect(url_for("auth.login"))
