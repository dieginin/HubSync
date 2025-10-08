import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "HubSync"

SECRET_KEY = os.environ.get("SECRET_KEY")
DB_NAME = "database.db"

MIN_LENGTHS = {"email": 5, "name": 2, "password": 3, "username": 2}

MAIL_CONFIG = {
    "SERVER": os.environ.get("MAIL_SERVER", "smtp.example.com"),
    "PORT": int(os.environ.get("MAIL_PORT", 587)),
    "USERNAME": os.environ.get("MAIL_USERNAME", ""),
    "PASSWORD": os.environ.get("MAIL_PASSWORD", ""),
    "AUTHOR": f"Auth {APP_NAME}",
    "SENDER": "no-reply@nextbale.com",
}
