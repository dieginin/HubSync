from flask import Blueprint, render_template

from website.utils import login_required

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home() -> str:
    return render_template("home.html")
