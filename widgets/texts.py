from flet import FontWeight, Text, TextAlign


class _CustomText(Text):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.text_align = TextAlign.CENTER


class TitleText(_CustomText):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.color = "primary"
        self.size = 74
        self.weight = FontWeight.BOLD


class SubtitleText(_CustomText):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.color = "inverseprimary"
        self.size = 43
        self.weight = FontWeight.W_400


class RegularText(_CustomText):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.color = "onsurface"
        self.size = 14
        self.weight = FontWeight.W_100
