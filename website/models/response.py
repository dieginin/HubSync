from dataclasses import dataclass

from website.utils import ResponseType


@dataclass
class Response[T]:
    type: ResponseType
    message: str
    data: T | None = None
