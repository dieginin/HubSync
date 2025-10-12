from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from website import db
from website.utils import Role


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    display_name = db.Column(db.String(150))
    password = db.Column(db.String(256))
    role = db.Column(db.String(10))

    def __init__(
        self,
        display_name: str,
        email: str,
        username: str,
        password: str,
        role: Role = "member",
    ) -> None:
        super().__init__()
        self.display_name = display_name
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

    def is_admin(self) -> bool:
        return self.role == "admin" or self.role == "superadmin"

    def __repr__(self) -> str:
        return f"<User: {self.username}>"

    def __str__(self) -> str:
        return self.display_name
