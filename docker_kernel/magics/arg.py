import re

from typing import Callable

from .magic import Magic
from .helper.errors import MagicError
from .helper.types import FlagDict

class Arg(Magic):
    """Manipulate Build Arguments"""
    def __init__(self, kernel, *args, **flags):
        super().__init__(kernel, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["Command"], 1)
    
    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}
    
    @staticmethod
    def VALID_OPTIONS() -> dict[str, FlagDict]:
        return         {
            "remove": {
                "short": "rm",
                "default": None,
                "desc": "Remove the build argument specified by name"
            }
        }
    
    def _execute_magic(self) -> None:
        if self._args[0].lower()=="list" or self._args[0].lower()=="ls":
            self._kernel.send_response(f"Current build arguments:\n{str(self._kernel._buildargs)}")
        elif "remove" in self._args:
            key = self._args[1]
            if self._kernel.set_buildargs(True, **{key: None}):
                self._kernel.send_response(f"Build argument '{key}' removed\n")
                self._kernel.send_response(f"Current build arguments:\n{str(self._kernel.get_buildargs())}")
        else:
            for arg in self._args:
                if not re.match("^[^\s]+=[^\s]+$", arg):
                    raise MagicError(f"'{arg}' does not match input format, expected format: 'foo=bar'")

            for arg in self._args:
                name, value = arg.split("=")
                self._kernel.set_buildargs(False, **{name: value})
                self._kernel.send_response(f"Build argument '{name}' set to '{value}'\n")
                self._kernel.send_response(f"Current build arguments:\n{str(self._kernel.get_buildargs())}")

