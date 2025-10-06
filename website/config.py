import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
DB_NAME = "database.db"

MIN_EMAIL_LENGTH = 5
MIN_NAME_LENGTH = 2
MIN_PASSWORD_LENGTH = 3
MIN_USERNAME_LENGTH = 2
