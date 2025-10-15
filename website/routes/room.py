from flask import Blueprint as _Blueprint
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug import Response

from website import db_manager

room = _Blueprint("room", __name__)


@room.route("/layouts", methods=["GET", "POST"])
@login_required
def layouts() -> str:
    from website.models import Room

    if request.method == "POST":
        name = request.form.get("name", "").strip().upper()
        response = db_manager.create_room(name)
        flash(response.message, response.type)
    return render_template("room/layouts.html", rooms=Room.query.all())


@room.route("/layouts/<int:room_id>", methods=["GET", "POST"])
@login_required
def view_room(room_id: int) -> str:
    if request.method == "POST":
        new_name = request.form.get("name", "").strip().upper()
        response = db_manager.update_room_name(room_id, new_name)
        flash(response.message, response.type)
    return render_template("room/room.html", room=db_manager.get_room_by_id(room_id))


@room.route("/layouts/delete/<int:room_id>", methods=["POST"])
@login_required
def delete_room(room_id: int) -> Response:
    response = db_manager.delete_room(room_id)
    flash(response.message, response.type)
    return redirect(url_for("room.layouts"))


@room.route("/layouts/<int:room_id>/add_tray", methods=["GET", "POST"])
@login_required
def add_tray(room_id: int) -> Response:
    if request.method == "POST":
        tray_name = request.form.get("name", "").strip().upper()
        num_of_lights = request.form.get("num_of_lights", 4, type=int)
        width = request.form.get("width", 3, type=int)
        height = request.form.get("height", 3, type=int)
        response = db_manager.add_tray_to_room(
            room_id, tray_name, num_of_lights, width, height
        )
        flash(response.message, response.type)
    return redirect(url_for("room.view_room", room_id=room_id))
