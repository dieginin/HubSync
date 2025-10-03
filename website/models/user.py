from dataclasses import dataclass

from website.utils import Role


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
            email=(
                data["user_metadata"]["email"]
                if "user_metadata" in data
                else data["email"]
            ),
            username=(
                data["user_metadata"]["username"]
                if "user_metadata" in data
                else data["username"]
            ),
            display_name=(
                data["user_metadata"]["display_name"]
                if "user_metadata" in data
                else data["display_name"]
            ),
            role=(
                data["user_metadata"]["role"]
                if "user_metadata" in data
                else data["role"]
            ),
        )
