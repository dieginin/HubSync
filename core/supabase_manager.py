import flet as ft
from supabase import create_client
from supabase_auth import Session

from models.response import Response
from models.user import User
from utils.config import INITIAL_PASSWORD, SUPABASE_KEY, SUPABASE_URL, TAGS
from utils.datatype import DataDict, Role
from utils.helpers import is_email

atk_tag, rtk_tag, exp_tag, uid_tag = TAGS


class SupabaseManager:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.auth = supabase.auth
        self.table = supabase.table

        self._restore_session()

    # ---------------------------- Properties ----------------------------
    @property
    def default_password(self) -> str:
        response = self.table("default_password").select("*").execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["password"]
        self.set_default_password(INITIAL_PASSWORD)
        return INITIAL_PASSWORD

    @property
    def user(self) -> User:
        user = self.auth.get_user()
        return (
            User.from_dict(user.model_dump()["user"])
            if user
            else User("0", "guest@example.com", "guest", "Guest", "user")
        )

    @property
    def session(self) -> Session | None:
        return self.auth.get_session()

    # ------------------------- Session Persistence -------------------------
    def _restore_session(self) -> None:
        try:
            access_token = self.page.client_storage.get(atk_tag)
            refresh_token = self.page.client_storage.get(rtk_tag)
            if access_token and refresh_token:
                self.auth.set_session(
                    access_token=access_token, refresh_token=refresh_token
                )
        except:
            self._clear_saved_session()

    def _save_current_session(self) -> None:
        current_session = self.session
        if current_session:
            self.page.client_storage.set(atk_tag, current_session.access_token)
            self.page.client_storage.set(rtk_tag, current_session.refresh_token)
            self.page.client_storage.set(exp_tag, current_session.expires_at)
            if current_session.user:
                self.page.client_storage.set(uid_tag, current_session.user.id)

    def _clear_saved_session(self) -> None:
        self.page.client_storage.remove(atk_tag)
        self.page.client_storage.remove(rtk_tag)
        self.page.client_storage.remove(exp_tag)
        self.page.client_storage.remove(uid_tag)

    # ---------------------------- Auth Methods ----------------------------
    def sign_up(
        self,
        email: str,
        username: str,
        display_name: str,
        role: Role,
        password: str | None = None,
    ) -> Response:
        password = password if password else self.default_password
        try:
            response = self.auth.sign_up({"email": email, "password": password})
            if response.user:
                try:
                    self.table("users").insert(
                        {
                            "id": response.user.id,
                            "email": email,
                            "username": username,
                            "display_name": display_name,
                            "role": role,
                        }
                    ).execute()
                except:
                    pass

                return Response(
                    "success",
                    "User registered successfully. Please check your email to confirm your account.",
                )
            else:
                return Response("error", "User registration failed")

        except Exception as e:
            error_msg = str(e).lower()
            if "already registered" in error_msg or "already exists" in error_msg:
                return Response("error", "Email already registered")
            elif "weak password" in error_msg:
                return Response("error", "Password is too weak")
            elif "invalid email" in error_msg:
                return Response("error", "Invalid email format")
            else:
                return Response("error", f"Registration failed: {str(e)}")

    def sign_in(self, email_or_username: str, password: str) -> Response:
        try:
            if is_email(email_or_username):
                self.auth.sign_in_with_password(
                    {"email": email_or_username, "password": password}
                )
                self._save_current_session()
                return Response(
                    "success",
                    f"Welcome back!",
                )
            else:
                try:
                    users_response = (
                        self.table("users")
                        .select("email")
                        .eq("username", email_or_username)
                        .execute()
                    )
                    if not users_response.data:
                        return Response("error", "Username not found")

                    email = users_response.data[0]["email"]
                    self.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    self._save_current_session()
                    return Response(
                        "success",
                        f"Welcome back!",
                    )
                except Exception as e:
                    return Response("error", "Please use your email address to sign in")

        except Exception as e:
            error_msg = str(e).lower()
            if "invalid login credentials" in error_msg:
                return Response("error", "Invalid email or password")
            elif "email not confirmed" in error_msg:
                return Response("error", "Please confirm your email address")
            else:
                return Response("error", "Sign in failed. Please try again.")

    def sign_out(self) -> Response:
        try:
            self.auth.sign_out()
            self._clear_saved_session()
            return Response("success", "User signed out successfully")
        except:
            return Response("error", "Failed to sign out")

    # ---------------------------- User Management ----------------------------
    def update_password(self, user_id: str, new_password: str) -> Response:
        try:
            self.auth.admin.update_user_by_id(user_id, {"password": new_password})
            return Response("success", "Password updated successfully")
        except Exception as e:
            return Response("error", f"Failed to update password: {str(e)}")

    def update_user(self, user_id: str, metadata: DataDict) -> Response:
        try:
            self.table("users").update(metadata).eq("id", user_id).execute()
            return Response("success", "User updated successfully")
        except Exception as e:
            return Response("error", f"Failed to update user: {str(e)}")

    # ---------------------------- CRUD Operations ----------------------------
    def insert(self, table: str, data: DataDict) -> Response:
        try:
            self.table(table).insert(data).execute()
            return Response("success", f"Data inserted into {table} successfully")
        except:
            return Response("error", "Failed to insert data")

    def update(self, table: str, filters: DataDict, data: DataDict) -> Response:
        query = self.table(table).update(data)
        for col, val in filters.items():
            query = query.eq(col, val)

        try:
            query.execute()
            return Response("success", f"Data in {table} updated successfully")
        except:
            return Response("error", "Failed to update data")

    def delete(self, table: str, filters: DataDict) -> Response:
        query = self.table(table).delete()
        for col, val in filters.items():
            query = query.eq(col, val)

        try:
            query.execute()
            return Response("success", f"Data deleted from {table} successfully")
        except:
            return Response("error", "Failed to delete data")

    def clear_table(self, table: str) -> Response:
        try:
            self.table(table).delete().neq("id", 0).execute()
            return Response("success", f"All data cleared from {table} successfully")
        except:
            return Response("error", "Failed to clear table data")

    # ---------------------------- Helper Methods ----------------------------
    def has_users(self) -> bool:
        try:
            response = self.table("users").select("id").limit(1).execute()
            return len(response.data) > 0 if response.data else False
        except:
            return False

    def set_default_password(self, password: str) -> Response:
        res = self.table("default_password").upsert({"password": password}).execute()
        if res.model_dump()["type"] != "success":
            return Response("error", "Failed to set default password")
        return Response("success", "Default password set successfully")
