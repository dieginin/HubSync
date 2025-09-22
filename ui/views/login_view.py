import flet as ft

from utils.helpers import error_snackbar, success_snackbar


class LoginView(ft.View):
    def __init__(self, page: ft.Page, sbmanager) -> None:
        from core.supabase_manager import SupabaseManager

        super().__init__()
        page.title = "HubSync ☉ Login"

        self.page: ft.Page = page
        self.sbmanager: SupabaseManager = sbmanager

        self.__init__config()
        self.__init_components__()

    def __init__config(self) -> None:
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.padding = 0

    def __init_components__(self) -> None:
        title = ft.Text("Login", size=32, weight=ft.FontWeight.BOLD)
        self.email_or_username = ft.TextField(
            enable_interactive_selection=True,
            autocorrect=True,
            enable_suggestions=True,
            label="Email or Username",
            keyboard_type=ft.KeyboardType.EMAIL,
            width=300,
            autofocus=True,
            can_request_focus=True,
            on_submit=self.login,
            autofill_hints=[ft.AutofillHint.EMAIL, ft.AutofillHint.USERNAME],
        )
        self.password = ft.TextField(
            enable_interactive_selection=True,
            autocorrect=True,
            enable_suggestions=True,
            label="Password",
            width=300,
            can_request_focus=True,
            password=True,
            can_reveal_password=True,
            on_submit=self.login,
            autofill_hints=ft.AutofillHint.PASSWORD,
        )
        login_button = ft.ElevatedButton("Login", width=300, on_click=self.login)

        self.controls = [
            title,
            ft.AutofillGroup(ft.Column([self.email_or_username, self.password])),
            login_button,
        ]

    def login(self, e: ft.ControlEvent) -> None:
        email_or_username = self.email_or_username.value
        password = self.password.value

        if not email_or_username or not password:
            error_snackbar(e.page, "Please fill in all fields.")
            if not email_or_username:
                self.email_or_username.focus()
            else:
                self.password.focus()
            return

        response = self.sbmanager.sign_in(email_or_username, password)

        if response.type == "success":
            e.page.go("/")
            success_snackbar(e.page, response.message)
        else:
            error_snackbar(e.page, response.message)
