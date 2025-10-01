from typing import Any, Literal

DataDict = dict[str, Any]

Role = Literal["superadmin", "admin", "user"]

ResponseType = Literal["success", "error"]
