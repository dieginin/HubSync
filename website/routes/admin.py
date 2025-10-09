from flask import Blueprint as _Blueprint
from flask import render_template
from flask_login import login_required

admin = _Blueprint("admin", __name__)


@admin.route("/staff")
@login_required
def staff() -> str:
    return render_template("staff.html")


@admin.route("/invox")
@login_required
def invox() -> str:
    return render_template("invox.html")
