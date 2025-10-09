from flask import Blueprint as _Blueprint
from flask import flash, render_template, request
from flask_login import current_user, login_required

from website import db_manager
from website.config import MIN_LENGTHS

main = _Blueprint("main", __name__)


@main.route("/")
@login_required
def home() -> str:
    return render_template("main/home.html")


@main.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> str:
    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "profile":
            display_name = request.form.get("display_name", "").strip()
            username = request.form.get("username", "")
            email = request.form.get("email", "")

            if len(display_name) < MIN_LENGTHS["name"]:
                flash(
                    f"Display name must be at least {MIN_LENGTHS['name']} characters long",
                    category="danger",
                )
            elif len(username) < MIN_LENGTHS["username"]:
                flash(
                    f"Username must be at least {MIN_LENGTHS['username']} characters long",
                    category="danger",
                )
            elif len(email) < MIN_LENGTHS["email"]:
                flash(f"Please enter a valid email address", category="danger")
            else:
                response = db_manager.update_user_profile(
                    user_id=current_user.id,
                    email=email,
                    username=username,
                    display_name=display_name,
                )
                flash(response.message, category=response.type)

        elif form_type == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if len(current_password) < 1:
                flash("Current password is required", category="danger")
            elif len(new_password) < MIN_LENGTHS["password"]:
                flash(
                    f"New password must be at least {MIN_LENGTHS['password']} characters long",
                    category="danger",
                )
            elif new_password != confirm_password:
                flash("New passwords do not match", category="danger")
            elif current_password == new_password:
                flash(
                    "New password must be different from current password",
                    category="danger",
                )
            else:
                response = db_manager.change_password(
                    current_password=current_password,
                    new_password=new_password,
                    email=current_user.email,
                )
                flash(response.message, category=response.type)

        elif form_type == "theme":
            theme = request.form.get("theme", "auto")

            if theme not in ["auto", "light", "dark"]:
                flash("Invalid theme selection", category="danger")
            else:
                flash("Theme preference saved successfully", category="success")
    return render_template("main/settings.html")
