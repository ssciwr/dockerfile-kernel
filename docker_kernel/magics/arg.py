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
        return ([], 0)
    
    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}
    
    @staticmethod
    def VALID_OPTIONS() -> dict[str, FlagDict]:
        return         {
            "remove": {
                "short": "rm",
                "default": "all",
                "desc": "Remove the build argument specified by name"
            },
            "list": {
                "short": "ls",
                "default": "all",
                "desc": "List the build argument(s) specified by name"
            }
        }
    
    def _execute_magic(self) -> None:

        for short in self._shorts.keys():
            match short.lower():
                case "rm":
                    self._remove_argument(self._shorts[short])
                case "ls":
                    self._list_argument(self._shorts[short])

        for flag in self._flags.keys():
            match flag.lower():
                case "remove":
                    self._remove_argument(self._flags[flag])
                case "list":
                    self._list_argument(self._flags[flag])

        if self._args:
            for arg in self._args:
                if not re.match("^[^\s]+=[^\s]+$", arg):
                    raise MagicError(f"'{arg}' does not match input format, expected format: '<name>=<value>'")

            for arg in self._args:
                name, value = arg.split("=")
                self._kernel.set_buildargs(False, **{name: value})
                self._kernel.send_response(f"Build argument '{name}' set to '{value}'\n")
            self._list_argument("all")

    def _remove_argument(self, arg):
        if arg == "all":
            self._kernel.reset_buildargs()
            self._kernel.send_response("All build arguments removed\n")  
        elif self._kernel.set_buildargs(True, **{arg: None}):
            self._kernel.send_response(f"Build argument '{arg}' removed\n")

    def _list_argument(self, arg):
        buildargs = self._kernel.get_buildargs()
        if arg == "all":
            if not buildargs:
                self._kernel.send_response("No current build arguments")
            else:
                self._kernel.send_response("Current build arguments:\n")
                for b in buildargs.keys():
                    self._kernel.send_response(f"\t{b}={buildargs[b]}\n")
        else:
            self._kernel.send_response(f"Current build argument:\n{arg}={buildargs[arg]}\n")
