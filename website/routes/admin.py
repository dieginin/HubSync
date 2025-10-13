from typing import cast

from flask import Blueprint as _Blueprint
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug import Response

from website.utils import admin_only

admin = _Blueprint("admin", __name__)

from website import db_manager
from website.utils import Role


@admin.route("/staff", methods=["GET", "POST"])
@login_required
@admin_only
def staff() -> Response | str:
    from website.models import User

    if request.method == "POST":
        name = request.form.get("name", "").strip().title()
        email = request.form.get("email", "")
        username = request.form.get("username", "")
        role = request.form.get("role", "member")
        VALID_ROLES = ["superadmin", "admin", "member"]
        selected_role = cast(Role, role if role in VALID_ROLES else "member")

        if db_manager.get_user_by_email(email):
            flash("Email already in use.", "danger")
        elif db_manager.get_user_by_username(username):
            flash("Username already in use.", "danger")
        else:
            db_manager.create_user(name, email, username, "carefree", selected_role)
            flash(f"User {name} created with default password 'carefree'", "success")
    return render_template("admin/staff.html", staff=User.query.all())


@admin.route("/staff/edit/<int:user_id>", methods=["POST"])
@login_required
@admin_only
def edit_staff_member(user_id: int) -> Response:
    name = request.form.get("display_name", "").strip().title()
    email = request.form.get("email", "")
    username = request.form.get("username", "")
    role = request.form.get("role", "member")
    VALID_ROLES = ["superadmin", "admin", "member"]
    selected_role = cast(Role, role if role in VALID_ROLES else "member")

    response = db_manager.update_user_profile(
        user_id, name, email, username, selected_role
    )
    flash(response.message, response.type)
    return redirect(url_for("admin.staff"))


@admin.route("/staff/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_only
def delete_staff_member(user_id: int) -> Response:
    response = db_manager.delete_user(user_id)
    flash(response.message, response.type)
    return redirect(url_for("admin.staff"))


@admin.route("/invox")
@login_required
@admin_only
def invox() -> str:
    return render_template("admin/invox.html")
