from datetime import datetime, timedelta

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from website import db


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column()
    used: Mapped[bool] = mapped_column()

    def __init__(self, token: str, user_id: int, expires_in_minutes: int = 30) -> None:
        self.token = token
        self.user_id = user_id
        self.expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        self.used = False

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

    def mark_as_used(self) -> None:
        self.used = True
        db.session.commit()
