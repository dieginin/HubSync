import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
DB_NAME = "database.db"

MIN_LENGTHS = {"email": 5, "name": 2, "password": 3, "username": 2}
