from typing import Optional

from postgrest import SyncRequestBuilder
from supabase import create_client
from supabase_auth import Session

from config import INITIAL_PASSWORD, SUPABASE_KEY, SUPABASE_URL
from website.models import Response
from website.utils import DataDict, Role, is_email


class DatabaseManager:
    def __init__(self) -> None:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.auth = supabase.auth
        self.table = supabase.table

    def set_session_from_tokens(self, access_token: str, refresh_token: str) -> bool:
        """Set the Supabase session using tokens, useful after page reload"""
        try:
            # Try to set the session using the tokens directly
            self.auth.set_session(access_token, refresh_token)
            return True
        except Exception as e:
            print(f"Could not set session from tokens: {e}")
            return False

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
    ) -> Response:
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

    def update_user_profile(
        self,
        user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> Response:
        try:
            if email:
                existing_email_user = self.get_user_by_eq("email", email)
                if existing_email_user and existing_email_user[0]["id"] != user_id:
                    return Response(type="error", message="Email already exists")

            if username:
                existing_username_user = self.get_user_by_eq("username", username)
                if (
                    existing_username_user
                    and existing_username_user[0]["id"] != user_id
                ):
                    return Response(type="error", message="Username already exists")

            update_data: DataDict = {}
            old_email = self.get_user_by_eq("id", user_id)[0]["email"]
            if email is not None:
                update_data["email"] = email
            if username is not None:
                update_data["username"] = username
            if display_name is not None:
                update_data["display_name"] = display_name

            self.users_table.update(update_data).eq("id", user_id).execute()

            # Only try to update auth email if email is being changed and we have an active session
            if email and email != old_email:
                try:
                    # Check if we have an active session, if not skip auth update
                    current_session = self.auth.get_session()
                    if current_session and current_session.access_token:
                        self.auth.update_user({"email": email})
                    # If no active session, we still update the database but skip auth update
                    # The auth email will be updated next time user logs in
                except Exception as auth_error:
                    auth_error_msg = str(auth_error)
                    # If it's just a missing session, don't revert - this is expected after page reload
                    if (
                        "Auth session missing" in auth_error_msg
                        or "session" in auth_error_msg.lower()
                    ):
                        # Just log this but don't fail the entire update
                        print(
                            f"Warning: Could not update auth email due to missing session: {auth_error_msg}"
                        )
                    else:
                        # For other auth errors, revert database changes
                        self.users_table.update({"email": old_email}).eq(
                            "id", user_id
                        ).execute()
                        return Response(
                            type="error",
                            message=f"Failed to update email in authentication system: {str(auth_error)}",
                        )

            return Response("success", "Profile updated successfully")
        except Exception as e:
            return Response("error", str(e))

    def change_password(
        self, current_password: str, new_password: str, email: str
    ) -> Response:
        try:
            try:
                self.auth.sign_in_with_password(
                    {"email": email, "password": current_password}
                )
            except Exception:
                return Response("error", "Current password is incorrect")

            self.auth.update_user({"password": new_password})
            return Response("success", "Password changed successfully")
        except Exception as e:
            error_msg = str(e).lower()
            if "weak password" in error_msg or "password" in error_msg:
                return Response("error", "New password is too weak")
            else:
                return Response("error", str(e))
