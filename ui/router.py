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
        page.on_connect = self.on_connect
        page.on_route_change = self.on_route_change
        self.sbmanager = sbmanager

        page.go("/")

    def _set_route(
        self,
        e: ft.RouteChangeEvent,
        route: str,
        condition: str,
        route_to: str | None = None,
    ) -> None:
        if e.route == route if condition == "==" else e.route != route:
            e.page.views.append(
                ROUTES.get(route, PageNotFoundView)(e.page, self.sbmanager)  # type: ignore
            )
        else:
            route = route_to if route_to else route
            e.page.go(route)

    def on_connect(self, e: ft.ControlEvent) -> None:
        if (
            len(self.sbmanager.auth.admin.list_users()) == 0
            and e.page.route != "/first"
        ):
            e.page.go("/first")
        elif not self.sbmanager.session and e.page.route != "/login":
            e.page.go("/login")

    def on_route_change(self, e: ft.RouteChangeEvent) -> None:
        e.page.views.clear()
        if len(self.sbmanager.auth.admin.list_users()) >= 1 and e.route == "/first":
            e.page.go("/")

        if len(self.sbmanager.auth.admin.list_users()) == 0:
            self._set_route(e, "/first", "==")
        elif self.sbmanager.session:
            self._set_route(e, "/login", "!=", "/")
        else:
            self._set_route(e, "/login", "==")
        e.page.update()
