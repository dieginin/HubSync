import flet as ft


def main(page: ft.Page):
    page.title = "HubSync"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    count = int(page.client_storage.get("count") or 0)

    welcome = ft.Text("Welcome to HubSync!", style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    page.add(welcome)
    txt_number = ft.TextField(
        value=str(count), text_align=ft.TextAlign.RIGHT, width=100
    )

    def minus_click(e):
        txt_number.value = str(int(txt_number.value or 0) - 1)
        page.client_storage.set("count", txt_number.value)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value or 0) + 1)
        page.client_storage.set("count", txt_number.value)
        page.update()

    page.add(
        ft.Row(
            [
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                txt_number,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


ft.app(target=main)
