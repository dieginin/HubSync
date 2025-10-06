from flask import Blueprint as _Blueprint
from flask import render_template
from flask_login import current_user, login_required

main = _Blueprint("main", __name__)


@main.route("/")
@login_required
def home() -> str:
    return render_template("home.html")
