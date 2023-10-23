from typing import TypedDict, Any


class FlagDict(TypedDict):
    """Helper type for Magic flags.

    - *short*, if provided, will be an abbreviation for this flag
    - *default*, if provided, will be the default value for this flag
    - *desc*, is a description of the flag
    """

    short: str | None
    default: Any | None
    desc: str
