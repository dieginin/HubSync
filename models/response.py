from dataclasses import dataclass

from utils.datatype import ResponseType


@dataclass
class Response:
    type: ResponseType
    message: str
