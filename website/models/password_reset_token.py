from datetime import datetime, timedelta

from website import db


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    expires_at = db.Column(db.DateTime)
    used = db.Column(db.Boolean)

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
