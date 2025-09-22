from dataclasses import dataclass

from utils.datatype import Role


@dataclass
class User:
    id: str
    email: str
    username: str
    display_name: str
    role: Role

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            email=data["user_metadata"]["email"],
            username=data["user_metadata"]["username"],
            display_name=data["user_metadata"]["display_name"],
            role=data["user_metadata"]["role"],
        )
