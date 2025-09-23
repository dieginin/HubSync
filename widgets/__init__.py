from flet import Container


class Spacer(Container):
    def __init__(self, flex: int = 1) -> None:
        super().__init__()
        self.expand = flex
