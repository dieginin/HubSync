from flask import Blueprint as _Blueprint
from flask import render_template
from flask_login import login_required

team = _Blueprint("team", __name__)


@team.route("/schedule")
@login_required
def schedule() -> str:
    return render_template("team/schedule.html")


@team.route("/tasks")
@login_required
def tasks() -> str:
    return render_template("team/tasks.html")
