import flet as ft

from core.supabase_manager import SupabaseManager
from ui.router import Router


def main(page: ft.Page) -> None:
    page.scroll = ft.ScrollMode.ADAPTIVE

    Router(page, SupabaseManager(page))


ft.app(target=main)
