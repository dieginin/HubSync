import re

from flask import Blueprint as _Blueprint
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug import Response
from werkzeug.security import check_password_hash

from website import db
from website.config import (
    MIN_EMAIL_LENGTH,
    MIN_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)
from website.models import User
from website.utils import first_setup_only, login_only_if_configured

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

        email_exists = User.query.filter(User.email == email).first()
        user_exists = User.query.filter(User.username == username).first()

        if email_exists:
            flash("Email already exists", category="danger")
        elif user_exists:
            flash("Username already exists", category="danger")
        elif len(name) < MIN_NAME_LENGTH:
            flash(
                f"Name must be at least {MIN_NAME_LENGTH} characters long",
                category="danger",
            )
        elif len(email) < MIN_EMAIL_LENGTH:
            flash(f"Please enter a valid email address", category="danger")
        elif len(username) < MIN_USERNAME_LENGTH:
            flash(
                f"Username must be at least {MIN_USERNAME_LENGTH} characters long",
                category="danger",
            )
        elif len(password) < MIN_PASSWORD_LENGTH:
            flash(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long",
                category="danger",
            )
        elif password != password2:
            flash("Passwords don't match", category="danger")
        else:
            new_user = User(
                display_name=name,
                email=email,
                username=username,
                role="superadmin",
                password=password,
            )
            db.session.add(new_user)
            db.session.commit()
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
            user = User.query.filter(User.email == email_or_username).first()
        else:
            user = User.query.filter(User.username == email_or_username).first()

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


@auth.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    flash("Logout successful", category="success")
    return redirect(url_for("auth.login"))
