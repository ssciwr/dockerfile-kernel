from typing import Callable

from .magic import Magic
from .helper.types import FlagDict

class Arg(Magic):
    """Manipulate Build Arguments"""
    def __init__(self, kernel, *args, **flags):
        super().__init__(kernel, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["ARG_name", "ARG_value"], 1)
    
    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}
    
    @staticmethod
    def VALID_OPTIONS() -> dict[str, FlagDict]:
        return {}
    
    def _execute_magic(self) -> None:
        for arg in self._args:
            name, value = arg.split("=")
            self._kernel.set_buildargs(**dict(name = value))
            self._kernel.send_response(f"Build argument '{name}' set to '{value}'")

