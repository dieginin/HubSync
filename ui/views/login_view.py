import flet as ft


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
            label="Email or Username",
            keyboard_type=ft.KeyboardType.EMAIL,
            width=300,
            autofocus=True,
            on_submit=self.login,
        )
        self.password = ft.TextField(
            label="Password",
            width=300,
            password=True,
            can_reveal_password=True,
            on_submit=self.login,
        )
        login_button = ft.ElevatedButton("Login", width=300, on_click=self.login)

        self.controls = [title, self.email_or_username, self.password, login_button]

    def login(self, e: ft.ControlEvent) -> None:
        email_or_username = self.email_or_username.value
        password = self.password.value

        if not email_or_username or not password:
            e.page.open(
                ft.SnackBar(
                    ft.Text("Please fill in all fields."), bgcolor=ft.Colors.RED_400
                )
            )
            if not email_or_username:
                self.email_or_username.focus()
            else:
                self.password.focus()
            return

        response = self.sbmanager.sign_in(email_or_username, password)

        if response.type == "success":
            e.page.go("/")
            e.page.open(
                ft.SnackBar(ft.Text(response.message), bgcolor=ft.Colors.GREEN_400)
            )
        else:
            e.page.open(
                ft.SnackBar(ft.Text(response.message), bgcolor=ft.Colors.RED_400)
            )
