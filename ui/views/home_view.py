import flet as ft

from utils.helpers import error_snackbar, success_snackbar


class HomeView(ft.View):
    def __init__(self, page: ft.Page, sbmanager) -> None:
        from core.supabase_manager import SupabaseManager

        super().__init__()
        page.title = "HubSync"

        self.page: ft.Page = page
        self.sbmanager: SupabaseManager = sbmanager

        self.__init__config__()
        self.__init_components__()

    def __init__config__(self) -> None:
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.padding = 0

    def __init_components__(self) -> None:
        title = ft.Text(
            f"Welcome {self.sbmanager.user.display_name}",
            size=32,
            weight=ft.FontWeight.BOLD,
        )
        logout_button = ft.ElevatedButton("Logout", width=300, on_click=self.logout)

        self.controls = [title, logout_button]

    def logout(self, e: ft.ControlEvent) -> None:
        res = self.sbmanager.sign_out()
        if res.type == "success":
            e.page.go("/login")
            success_snackbar(e.page, res.message)
        else:
            error_snackbar(e.page, res.message)
