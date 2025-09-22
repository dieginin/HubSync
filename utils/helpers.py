import os
import re

from flet import Page, SnackBar, Text, TextAlign, View

email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
is_email = lambda x: bool(re.match(email_regex, x))


def get_routes(directory: str) -> dict[str, type[View]]:
    routes = {}
    folder = "ui"

    for file in os.listdir(os.path.join(folder, directory)):
        if file.endswith(".py"):
            module_name = file[:-3]
            module = __import__(
                f"{folder}.{directory}.{module_name}", fromlist=[module_name]
            )

            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if isinstance(attr, type) and issubclass(attr, View) and attr != View:
                    route = "/" + attr_name.lower()

                    if route.endswith("view"):
                        route = route[:-4]
                    if route == "/home":
                        route = "/"

                    routes[route] = attr
    return routes


def _show_snackbar(page: Page, message: str, message_color: str, bgcolor: str) -> None:
    page.open(
        SnackBar(
            Text(
                message,
                text_align=TextAlign.CENTER,
                color=message_color,
            ),
            bgcolor=bgcolor,
        )
    )


def success_snackbar(page: Page, message: str) -> None:
    color = "primary"
    _show_snackbar(page, message, f"on{color}", color)


def error_snackbar(page: Page, message: str) -> None:
    color = "error"
    _show_snackbar(page, message, f"on{color}", color)
