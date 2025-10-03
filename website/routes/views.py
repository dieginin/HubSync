from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug import Response

from website import db
from website.utils import login_required

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home() -> str:
    return render_template("home.html")


@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> Response | str:
    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "profile":
            # Handle profile update
            display_name = request.form.get("display_name", "").strip()
            username = request.form.get("username", "")
            email = request.form.get("email", "")

            # Validation
            if len(display_name) < 2:
                flash(
                    "Display name must be at least 2 characters long", category="danger"
                )
            elif len(username) < 2:
                flash("Username must be at least 2 characters long", category="danger")
            elif len(email) < 5:
                flash("Please enter a valid email address", category="danger")
            else:
                response = db.update_user_profile(
                    user_id=g.user.id,
                    email=email,
                    username=username,
                    display_name=display_name,
                )
                flash(
                    response.message,
                    category="success" if response.type == "success" else "danger",
                )

                if response.type == "success":
                    from website.models import User

                    user_data = db.get_user_by_eq("id", g.user.id)
                    if user_data:
                        g.user = User(
                            id=user_data[0]["id"],
                            email=user_data[0]["email"],
                            username=user_data[0]["username"],
                            display_name=user_data[0]["display_name"],
                            role=user_data[0]["role"],
                        )
                    return redirect(url_for("views.settings"))

        elif form_type == "password":
            # Handle password change
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            # Validation
            if len(current_password) < 3:
                flash("Current password is required", category="danger")
            elif len(new_password) < 3:
                flash(
                    "New password must be at least 3 characters long", category="danger"
                )
            elif new_password != confirm_password:
                flash("New passwords do not match", category="danger")
            elif current_password == new_password:
                flash(
                    "New password must be different from current password",
                    category="danger",
                )
            else:
                response = db.change_password(
                    current_password=current_password,
                    new_password=new_password,
                    email=g.user.email,
                )
                flash(
                    response.message,
                    category="success" if response.type == "success" else "danger",
                )

                if response.type == "success":
                    return redirect(url_for("views.settings"))

        elif form_type == "theme":
            # Handle theme preference (now handled entirely by JavaScript and localStorage)
            theme = request.form.get("theme", "auto")

            if theme not in ["auto", "light", "dark"]:
                flash("Invalid theme selection", category="danger")
            else:
                # Theme is handled by JavaScript/localStorage, just show success message
                flash("Theme preference saved successfully", category="success")
                return redirect(url_for("views.settings"))

    return render_template("settings.html")
