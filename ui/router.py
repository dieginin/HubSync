import flet as ft

from core.supabase_manager import SupabaseManager
from utils.config import ROUTES


class PageNotFoundView(ft.View):
    def __init__(self, *_) -> None:
        super().__init__()
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.controls = [
            ft.Text("404", size=150, weight=ft.FontWeight.BOLD),
            ft.Text("Page Not Found", size=32, weight=ft.FontWeight.BOLD),
        ]
        self.floating_action_button = ft.FloatingActionButton(
            icon="home", on_click=lambda e: e.page.go("/")
        )


class Router:
    def __init__(self, page: ft.Page, sbmanager: SupabaseManager) -> None:
        page.on_route_change = self.on_route_change
        self.sbmanager = sbmanager

        if self.sbmanager.session:
            page.go("/")
        else:
            page.go("/login")

    def on_route_change(self, e: ft.RouteChangeEvent) -> None:
        e.page.views.clear()

        if self.sbmanager.session:
            if e.route != "/login":
                e.page.views.append(
                    ROUTES.get(e.route, PageNotFoundView)(e.page, self.sbmanager)  # type: ignore
                )
            else:
                e.page.go("/")
        else:
            if e.route == "/login":
                e.page.views.append(
                    ROUTES.get("/login", PageNotFoundView)(e.page, self.sbmanager)  # type: ignore
                )
            else:
                e.page.go("/login")

        e.page.update()
