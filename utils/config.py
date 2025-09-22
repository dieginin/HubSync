import os

import dotenv

from .helpers import get_routes

dotenv.load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

INITIAL_PASSWORD = "carefree"

ROUTES = get_routes("views")

TAGS = ("access_token", "refresh_token", "expires_at", "user_id")
