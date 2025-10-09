from flask import Blueprint as _Blueprint
from flask import render_template
from flask_login import login_required

room = _Blueprint("room", __name__)


@room.route("/layouts")
@login_required
def layouts() -> str:
    return render_template("layouts.html")
