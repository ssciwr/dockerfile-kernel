from typing import TypedDict, Any

class FlagDict(TypedDict):
        short: str | None
        default: Any
        desc: str