from typing import TypedDict, Any

class FlagDict(TypedDict):
        name: str
        short: str | None
        default: Any
        desc: str