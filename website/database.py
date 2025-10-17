from typing import TYPE_CHECKING

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from website.utils import Role

if TYPE_CHECKING:
    from website.models import PasswordResetToken, Room, User


class Response:
    def __init__(self, type: str, message: str) -> None:
        self.type = type
        self.message = message


class DatabaseManager:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def has_users(self) -> bool:
        from website.models import User

        return self.db.session.query(User).first() is not None

    def get_user_by_id(self, user_id: int) -> "User | None":
        from website.models import User

        return User.query.get(user_id)

    def get_user_by_email(self, email: str) -> "User | None":
        from website.models import User

        return User.query.filter_by(email=email).first()

    def get_user_by_username(self, username: str) -> "User | None":
        from website.models import User

        return User.query.filter_by(username=username).first()

    def create_user(
        self, display_name: str, email: str, username: str, password: str, role: Role
    ) -> "User":
        from website.models import User

        new_user = User(
            display_name=display_name,
            email=email,
            username=username,
            password=password,
            role=role,
        )
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_user

    def delete_user(self, user_id: int) -> Response:
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return Response(type="danger", message="User not found")

            if user_id == 1:
                return Response(
                    type="danger", message="Cannot delete the primary admin user"
                )

            self.db.session.delete(user)
            self.db.session.commit()
            return Response(
                type="success", message=f"{user.display_name} deleted successfully"
            )

        except Exception as e:
            self.db.session.rollback()
            return Response(type="danger", message=f"Error deleting user: {str(e)}")

    def update_user_profile(
        self,
        user_id: int,
        display_name: str,
        email: str,
        username: str,
        role: Role | None = None,
    ) -> Response:
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return Response(type="danger", message="User not found")

            existing_email_user = self.get_user_by_email(email)
            existing_username_user = self.get_user_by_username(username)
            if existing_email_user and existing_email_user.id != user_id:
                return Response(type="danger", message="Email already exists")
            if existing_username_user and existing_username_user.id != user_id:
                return Response(type="danger", message="Username already exists")

            user.email = email
            user.username = username
            user.display_name = display_name
            if role:
                user.role = role

            self.db.session.commit()
            return Response(type="success", message="Profile updated successfully")

        except Exception as e:
            self.db.session.rollback()
            return Response(type="danger", message=f"Error updating profile: {str(e)}")

    def change_password(
        self, current_password: str, new_password: str, email: str
    ) -> Response:
        try:
            user = self.get_user_by_email(email)
            if not user:
                return Response(type="danger", message="User not found")

            if not check_password_hash(user.password, current_password):
                return Response(type="danger", message="Current password is incorrect")

            user.password = generate_password_hash(new_password)
            self.db.session.commit()

            return Response(type="success", message="Password changed successfully")

        except Exception as e:
            self.db.session.rollback()
            return Response(type="danger", message=f"Error changing password: {str(e)}")

    def reset_password(self, new_password: str, email: str) -> Response:
        try:
            user = self.get_user_by_email(email)
            if not user:
                return Response(type="danger", message="User not found")

            user.password = generate_password_hash(new_password)
            self.db.session.commit()

            return Response(type="success", message="Password reset successfully")

        except Exception as e:
            self.db.session.rollback()
            return Response(
                type="danger", message=f"Error resetting password: {str(e)}"
            )

    def generate_reset_password_token(self, user: "User") -> str:
        import secrets

        from website.models import PasswordResetToken

        token = secrets.token_urlsafe(32)

        reset_token = PasswordResetToken(token, user.id)
        self.db.session.add(reset_token)
        self.db.session.commit()

        return token

    def verify_reset_password_token(
        self, token: str
    ) -> tuple[str, "PasswordResetToken"] | tuple[None, None]:
        from website.models import PasswordResetToken

        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if not reset_token or reset_token.used:
            return None, None
        if reset_token.is_expired():
            self.db.session.delete(reset_token)
            self.db.session.commit()
            return None, None

        user = self.get_user_by_id(reset_token.user_id)
        return (user.email, reset_token) if user else (None, None)

    def get_room_by_id(self, room_id: int) -> "Room | None":
        from website.models import Room

        return Room.query.get(room_id)

    def create_room(self, name: str) -> Response:
        from website.models import Room

        try:
            if Room.query.filter_by(name=name).first():
                return Response(type="danger", message="Room already exists")
            new_room = Room(name)
            self.db.session.add(new_room)
            self.db.session.commit()
            return Response(type="success", message=f"Room {name} created successfully")

        except Exception as e:
            self.db.session.rollback()
            return Response(type="danger", message=f"Error creating room: {str(e)}")

    def delete_room(self, room_id: int) -> Response:
        try:
            room = self.get_room_by_id(room_id)
            if not room:
                return Response(type="danger", message="Room not found")

            self.db.session.delete(room)
            self.db.session.commit()
            return Response(
                type="success", message=f"Room {room.name} deleted successfully"
            )

        except Exception as e:
            self.db.session.rollback()
            return Response(type="danger", message=f"Error deleting room: {str(e)}")

    def update_room_name(self, room_id: int, new_name: str) -> Response:
        from website.models import Room

        try:
            room = self.get_room_by_id(room_id)
            if not room:
                return Response(type="danger", message="Room not found")

            if Room.query.filter_by(name=new_name).first():
                return Response(type="danger", message="Room name already exists")

            room.name = new_name
            self.db.session.commit()
            return Response(
                type="success", message=f"Room {new_name} updated successfully"
            )

        except Exception as e:
            self.db.session.rollback()
            return Response(
                type="danger", message=f"Error updating room name: {str(e)}"
            )

    def add_tray_to_room(
        self, room_id: int, tray_name: str, num_of_lights: int, width: int, height: int
    ) -> Response:
        from website.models import Tray

        try:
            room = self.get_room_by_id(room_id)
            if not room:
                return Response(type="danger", message="Room not found")

            tray = Tray(room.id, tray_name, num_of_lights, width, height)
            self.db.session.add(tray)
            self.db.session.commit()
            return Response(
                type="success",
                message=f"Tray {tray_name} added to {room.name} successfully",
            )

        except Exception as e:
            self.db.session.rollback()
            return Response(
                type="danger", message=f"Error adding tray to room: {str(e)}"
            )

    def edit_tray(
        self, tray_id: int, tray_name: str, num_of_lights: int, width: int, height: int
    ) -> Response:
        from website.models import Tray

        try:
            tray = Tray.query.get(tray_id)
            if not tray:
                return Response(type="danger", message="Tray not found")

            tray.name = tray_name
            light = tray.lights[0]

            diff = len(tray.lights) - num_of_lights
            if diff > 0:
                tray.lights = tray.lights[0 : len(tray.lights) - diff]
            elif diff < 0:
                tray.add_lights(abs(diff), light.width, light.height)

            if light.width != width or light.height != height:
                room_id = tray.room_id
                self.delete_tray(tray_id)
                self.add_tray_to_room(room_id, tray_name, num_of_lights, width, height)

            self.db.session.commit()
            return Response(
                type="success",
                message=f"Tray {tray_name} updated successfully",
            )

        except Exception as e:
            self.db.session.rollback()
            return Response(type="danger", message=f"Error updating tray: {str(e)}")

    def delete_tray(self, tray_id: int) -> Response:
        from website.models import Tray

        try:
            tray = Tray.query.get(tray_id)
            if not tray:
                return Response(type="danger", message="Tray not found")

            self.db.session.delete(tray)
            self.db.session.commit()
            return Response(
                type="success", message=f"Tray {tray.name} deleted successfully"
            )

        except Exception as e:
            self.db.session.rollback()
            return Response(type="danger", message=f"Error deleting tray: {str(e)}")

    # Database Management Methods
    def create_tables(self, app: Flask) -> None:
        with app.app_context():
            self.db.create_all()

    def drop_tables(self, app: Flask) -> None:
        with app.app_context():
            self.db.drop_all()

    def reset_database(self, app: Flask) -> None:
        self.drop_tables(app)
        self.create_tables(app)
