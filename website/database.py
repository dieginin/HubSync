from typing import TYPE_CHECKING

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from website.utils import Role

if TYPE_CHECKING:
    from website.models import User


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

        return self.db.session.get(User, user_id)

    def get_user_by_email(self, email: str) -> "User | None":
        from website.models import User

        return self.db.session.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> "User | None":
        from website.models import User

        return self.db.session.query(User).filter(User.username == username).first()

    def create_user(
        self,
        display_name: str,
        email: str,
        username: str,
        password: str,
        role: Role = "user",
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

    def update_user_profile(
        self, user_id: int, email: str, username: str, display_name: str
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
                return Response(type="error", message="User not found")

            if not check_password_hash(user.password, current_password):
                return Response(type="error", message="Current password is incorrect")

            user.password = generate_password_hash(new_password)
            self.db.session.commit()

            return Response(type="success", message="Password changed successfully")

        except Exception as e:
            self.db.session.rollback()
            return Response(type="error", message=f"Error changing password: {str(e)}")

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
