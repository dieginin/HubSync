import flet as ft

from utils.helpers import error_snackbar, success_snackbar
from widgets import Spacer
from widgets.text_fields import (
    EmailField,
    NameField,
    PasswordField,
    RepeatPasswordField,
    UsernameField,
)
from widgets.texts import RegularText, SubtitleText, TitleText


class FirstView(ft.View):
    def __init__(self, page: ft.Page, sbmanager) -> None:
        from core.supabase_manager import SupabaseManager

        super().__init__()
        page.title = "HubSync ☉ First Time Setup"

        self.page: ft.Page = page
        self.sbmanager: SupabaseManager = sbmanager

        self.__init__config__()
        self.__init_field_form__()
        self.__init_components__()

    def __init__config__(self) -> None:
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.padding = 0

    def __init_field_form__(self) -> None:
        self.name = NameField(True, on_submit=self.initialize_admin_account)
        self.email = EmailField(on_submit=self.initialize_admin_account)
        self.username = UsernameField(new=True, on_submit=self.initialize_admin_account)
        self.password = PasswordField(new=True, on_submit=self.initialize_admin_account)
        self.repeat_password = RepeatPasswordField(
            self.password, on_submit=self.initialize_admin_account
        )
        self.form = ft.AutofillGroup(
            ft.Column(
                [
                    self.name,
                    self.email,
                    self.username,
                    self.password,
                    self.repeat_password,
                ],
                spacing=10,
            )
        )

    def __init_components__(self) -> None:
        logo = ft.Image(src="icon.png", width=225, height=225, fit=ft.ImageFit.CONTAIN)
        title = TitleText("HubSync")
        subtitle = SubtitleText("First Time Setup")
        description = RegularText(
            "It seems like this is your first time running HubSync\n"
            "Let's create your admin account to get started"
        )
        create_button = ft.ElevatedButton(
            text="Create Admin Account",
            width=200,
            on_click=self.initialize_admin_account,
        )

        self.controls = [
            Spacer(5),
            logo,
            title,
            Spacer(1),
            subtitle,
            description,
            Spacer(2),
            self.form,
            Spacer(2),
            create_button,
            Spacer(7),
        ]

    def initialize_admin_account(self, _) -> None:
        form_data = {
            "name": self.name.value or "",
            "email": self.email.value or "",
            "username": self.username.value or "",
            "password": self.password.value or "",
            "confirm_password": self.repeat_password.value or "",
        }
        if not all(form_data.values()):
            error_snackbar(self.page, "Please fill in all fields")

        if not self._validate_individual_fields():
            return

        if form_data["password"] != form_data["confirm_password"]:
            error_snackbar(self.page, "Passwords do not match")
            return self.repeat_password.focus()

        self._create_account(form_data)

    def _validate_individual_fields(self) -> bool:
        field_configs = [
            (self.name, "Name is required"),
            (self.email, "Email is required"),
            (self.username, "Username is required"),
            (self.password, "Password is required"),
            (self.repeat_password, "Repeat Password is required"),
        ]
        first_error_field = None
        has_errors = False

        for field, error_message in field_configs:
            if not field.value:
                field.set_error(error_message)
                has_errors = True
                if first_error_field is None:
                    first_error_field = field

        if first_error_field:
            first_error_field.focus()

        return not has_errors

    def _create_account(self, form_data: dict[str, str]) -> None:
        response = self.sbmanager.sign_up(
            form_data["email"],
            form_data["username"],
            form_data["name"],
            "admin",
            form_data["password"],
        )

        if response.type == "success":
            success_snackbar(self.page, response.message)
            self.page.go("/login")
        else:
            error_snackbar(self.page, response.message)
