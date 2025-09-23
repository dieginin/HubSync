from typing import Callable

import flet as ft

from utils.helpers import is_email

_EMAIL_REGEX = r"^(?!@)[A-Za-z0-9._%+\-]*(?:@(?!\.)[A-Za-z0-9._%+\-]*)?$"
_NAME_REGEX = r"^(?![ .\-'])(?!.*(?:[ \-'][ .\-']|\.[.\-']))[A-Za-z .\-']*$"
_NUMBER_REGEX = r"^(?!.*\..*\.)[0-9.]*$"
_PASSWORD_REGEX = r"^[^ ]*$"
_TEXT_REGEX = r"^[A-Za-z0-9 .,\-_'\"!?@#$%^&*()]*$"
_USERNAME_REGEX = r"^[A-Za-z0-9]*$"


class _CustomTextField(ft.TextField):
    def __init__(self) -> None:
        super().__init__()
        self.border = ft.InputBorder.UNDERLINE
        self.border_color = "onprimarycontainer"
        self.error_text = ""
        self.focused_border_color = "primary"
        self.label_style = ft.TextStyle(color="onprimarycontainer")
        self.max_length = 35
        self.on_blur = lambda _: self.clear_spaces()
        self.on_change = lambda _: self.clear_error()
        self.text_align = ft.TextAlign.CENTER
        self.width = 300

    def lower(self) -> None:
        self.value = self.value.lower() if self.value else ""
        self.clear_error()

    def set_error(self, message: str) -> None:
        self.label_style = ft.TextStyle(color="error")
        self.error_text = message
        self.update()

    def clear_spaces(self) -> None:
        self.value = self.value.strip() if self.value else ""
        self.update()

    def clear_error(self) -> None:
        self.label_style = ft.TextStyle(color="onprimarycontainer")
        self.error_text = ""
        self.update()


class EmailField(_CustomTextField):
    def __init__(
        self,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autocorrect = False
        self.autofill_hints = ft.AutofillHint.EMAIL
        self.autofocus = autofocus
        self.enable_suggestions = False
        self.hint_text = hint_text or "Your email"
        self.input_filter = ft.InputFilter(_EMAIL_REGEX)
        self.keyboard_type = ft.KeyboardType.EMAIL
        self.label = "Email"
        self.on_change = lambda _: self.lower()
        self.on_blur = lambda _: self.verify()
        self.on_submit = on_submit

    def verify(self) -> None:
        self.clear_spaces()
        if self.value and not is_email(self.value):
            self.set_error("Enter a valid email")


class EmailOrUsernameField(_CustomTextField):
    def __init__(
        self,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autocorrect = False
        self.autofill_hints = [ft.AutofillHint.EMAIL, ft.AutofillHint.USERNAME]
        self.autofocus = autofocus
        self.enable_suggestions = False
        self.hint_text = hint_text or "Your email or username"
        self.input_filter = ft.InputFilter(_EMAIL_REGEX)
        self.keyboard_type = ft.KeyboardType.EMAIL
        self.label = "Email or Username"
        self.on_change = lambda _: self.lower()
        self.on_blur = lambda _: self.verify()
        self.on_submit = on_submit

    def verify(self) -> None:
        self.clear_spaces()
        if self.value and "@" in self.value:
            if not is_email(self.value):
                self.set_error("Enter a valid email")
        else:
            if self.value and len(self.value) <= 2:
                self.set_error("Username must be at least 3 characters")


class NameField(_CustomTextField):
    def __init__(
        self,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autocorrect = False
        self.autofill_hints = ft.AutofillHint.NAME
        self.autofocus = autofocus
        self.capitalization = ft.TextCapitalization.WORDS
        self.enable_suggestions = False
        self.hint_text = hint_text or "Your full name"
        self.input_filter = ft.InputFilter(_NAME_REGEX)
        self.keyboard_type = ft.KeyboardType.NAME
        self.label = "Name"
        self.on_submit = on_submit


class NumberField(_CustomTextField):
    def __init__(
        self,
        label: str,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autocorrect = False
        self.autofocus = autofocus
        self.enable_suggestions = False
        self.hint_text = hint_text
        self.input_filter = ft.InputFilter(_NUMBER_REGEX)
        self.keyboard_type = ft.KeyboardType.NUMBER
        self.label = label
        self.on_change = lambda _: self.refactor()
        self.on_submit = on_submit

    def refactor(self) -> None:
        if self.value:
            if len(self.value) == 1 and "." in self.value:
                self.value = "0."
            elif len(self.value) >= 2 and self.value[0] == "0" and self.value[1] != ".":
                self.value = self.value[1:]
        self.clear_error()


class PasswordField(_CustomTextField):
    def __init__(
        self,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        new: bool = False,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autocorrect = False
        self.autofill_hints = (
            ft.AutofillHint.NEW_PASSWORD if new else ft.AutofillHint.PASSWORD
        )
        self.autofocus = autofocus
        self.can_reveal_password = True
        self.enable_suggestions = False
        self.hint_text = hint_text or "Your password"
        self.input_filter = ft.InputFilter(_PASSWORD_REGEX)
        self.keyboard_type = ft.KeyboardType.VISIBLE_PASSWORD
        self.label = "Password"
        self.on_blur = lambda _: self.verify()
        self.on_submit = on_submit
        self.password = True

    def verify(self) -> None:
        self.clear_spaces()
        if self.value and len(self.value) <= 5:
            self.set_error("Password must be at least 6 characters")


class RegularField(_CustomTextField):
    def __init__(
        self,
        label: str,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autofocus = autofocus
        self.hint_text = hint_text
        self.keyboard_type = ft.KeyboardType.TEXT
        self.label = label
        self.on_submit = on_submit


class RepeatPasswordField(_CustomTextField):
    def __init__(
        self,
        password_field: PasswordField,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autocorrect = False
        self.autofill_hints = ft.AutofillHint.NEW_PASSWORD
        self.autofocus = autofocus
        self.can_reveal_password = True
        self.enable_suggestions = False
        self.hint_text = hint_text or "Repeat your password"
        self.input_filter = ft.InputFilter(_PASSWORD_REGEX)
        self.keyboard_type = ft.KeyboardType.VISIBLE_PASSWORD
        self.label = "Repeat Password"
        self.on_blur = lambda _: self.verify()
        self.on_change = lambda _: self.validate_password_match()
        self.on_submit = on_submit
        self.password = True
        self.password_field = password_field

        self._events_bound = False
        self._bind_password_field_events()

    def _bind_password_field_events(self) -> None:
        if getattr(self, "_events_bound", False):
            return

        def _on_pwd_change(e) -> None:
            if callable(prev_on_change):
                prev_on_change(e)
            self.validate_password_match()

        def _on_pwd_blur(e) -> None:
            if callable(prev_on_blur):
                prev_on_blur(e)
            self.validate_password_match()

        prev_on_change = self.password_field.on_change
        self.password_field.on_change = _on_pwd_change

        prev_on_blur = self.password_field.on_blur
        self.password_field.on_blur = _on_pwd_blur

        self._events_bound = True

    def validate_password_match(self) -> None:
        if self.value and self.value != (self.password_field.value or ""):
            self.set_error("Passwords do not match")
        else:
            self.clear_error()

    def verify(self) -> None:
        self.clear_spaces()
        if self.value:
            if len(self.value) <= 5:
                self.set_error("Password must be at least 6 characters")
            elif self.value != (self.password_field.value or ""):
                self.set_error("Passwords do not match")


class TextField(_CustomTextField):
    def __init__(
        self,
        label: str,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autofocus = autofocus
        self.hint_text = hint_text
        self.input_filter = ft.InputFilter(_TEXT_REGEX)
        self.keyboard_type = ft.KeyboardType.TEXT
        self.label = label
        self.on_submit = on_submit


class UsernameField(_CustomTextField):
    def __init__(
        self,
        autofocus: bool | None = None,
        hint_text: str | None = None,
        new: bool = False,
        on_submit: Callable | None = None,
    ) -> None:
        super().__init__()
        self.autocorrect = False
        self.autofill_hints = (
            ft.AutofillHint.NEW_USERNAME if new else ft.AutofillHint.USERNAME
        )
        self.autofocus = autofocus
        self.enable_suggestions = False
        self.hint_text = hint_text or "Your username"
        self.input_filter = ft.InputFilter(_USERNAME_REGEX)
        self.keyboard_type = ft.KeyboardType.NAME
        self.label = "Username"
        self.on_change = lambda _: self.lower()
        self.on_submit = on_submit
        self.on_blur = lambda _: self.verify()
        self.on_submit = on_submit

    def verify(self) -> None:
        self.clear_spaces()
        if self.value and len(self.value) <= 2:
            self.set_error("Username must be at least 3 characters")
