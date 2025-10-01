from postgrest import SyncRequestBuilder
from supabase import create_client
from supabase_auth import Session

from config import INITIAL_PASSWORD, SUPABASE_KEY, SUPABASE_URL
from website.models import Response, User
from website.utils import DataDict, Role, is_email


class DatabaseManager:
    def __init__(self) -> None:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.auth = supabase.auth
        self.table = supabase.table

    @property
    def users_table(self) -> SyncRequestBuilder[DataDict]:
        return self.table("users")

    @property
    def users_exist(self) -> bool:
        return len(self.users_table.select("*").execute().data) > 0

    def get_user_by_eq(self, eq: str, value: str) -> list[DataDict]:
        return self.users_table.select("*").eq(eq, value).execute().data

    def register(
        self,
        email: str,
        username: str,
        display_name: str,
        password: str = INITIAL_PASSWORD,
        role: Role = "user",
    ) -> Response[User]:
        if self.get_user_by_eq("email", email):
            return Response(type="error", message="Email already exists")
        if self.get_user_by_eq("username", username):
            return Response(type="error", message="Username already exists")

        try:
            data = self.auth.sign_up({"email": email, "password": password})
            if user := data.user:
                user_data: DataDict = {
                    "id": user.id,
                    "email": email,
                    "username": username,
                    "display_name": display_name,
                    "role": role,
                }
                self.users_table.insert(user_data).execute()
                return Response(
                    "success",
                    f"User registered successfully. Please check {email} to confirm the account",
                    User(**user_data),
                )
            return Response("error", "User registration failed")
        except Exception as e:
            return Response("error", str(e))

    def login(self, email_or_username: str, password: str) -> Response[Session]:
        if not is_email(email_or_username):
            user = self.get_user_by_eq("username", email_or_username)
            if not user:
                return Response(type="error", message="Username not found")
            email = user[0]["email"]
        else:
            if not self.get_user_by_eq("email", email_or_username):
                return Response(type="error", message="Email not found")
            email = email_or_username

        try:
            data = self.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if session := data.session:
                return Response("success", "Login successful", session)
            return Response("error", "Login failed")
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid login credentials" in error_msg:
                return Response("error", "Wrong password")
            elif "email not confirmed" in error_msg:
                return Response("error", "Please confirm your email address")
            else:
                return Response("error", str(e))

    def send_password_reset_email(self, email: str) -> Response:
        try:
            self.auth.reset_password_for_email(email)
            return Response("success", "Password reset email sent")
        except Exception as e:
            return Response("error", str(e))

    def refresh_session(self, refresh_token: str) -> Response[Session]:
        try:
            data = self.auth.refresh_session(refresh_token)
            if session := data.session:
                return Response("success", "Session refreshed successfully", session)
            return Response("error", "Could not refresh session")
        except Exception as e:
            return Response("error", str(e))

    def logout(self) -> Response:
        try:
            self.auth.sign_out()
            return Response("success", "Session closed successfully")
        except Exception as e:
            return Response("error", str(e))
