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
        return (["command"], 1)

    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}

    @staticmethod
    def VALID_FLAGS() -> dict[str, FlagDict]:
        return {}

    def _execute_magic(self) -> None:
        if self._args:
            for arg in self._args:
                match arg.lower():
                    case "rm" | "remove":
                        if len(self._args) == 1:
                            self._remove_argument()
                            return
                        self._kernel.send_response(self._args)
                        self._remove_argument(*self._args[1:])
                        return
                    case "ls" | "list":
                        if len(self._args) == 1:
                            self._list_argument()
                            return
                        self._kernel.send_response(self._args)
                        self._list_argument(*self._args[1:])
                        return

                if not re.match("^[^\s]+=[^\s]+$", arg):
                    raise MagicError(
                        f"'{arg}' does not match input format, expected format: '<name>=<value>'"
                    )

            for arg in self._args:
                name, value = arg.split("=")
                self._kernel._buildargs.update({name: value})
                self._kernel.send_response(
                    f"Build argument '{name}' set to '{value}'\n"
                )
            self._list_argument()

    def _remove_argument(self, *names: str):
        """Remove *build arguments* from `DockerKernel`.

        Args:
            *names (tuple[str]): The names of the *build arguments* to be removed.
        """
        if len(names) == 0:
            self._kernel.remove_buildargs()
            self._kernel.send_response("All build arguments removed\n")
        else:
            response = ""
            for name in names:
                if name in self._kernel._buildargs.keys():
                    response = response + f"Build argument '{name}' removed\n"
                    continue
                else:
                    self._kernel.send_response(
                        f"'{name}' not in current build arguments"
                    )
                    return
            self._kernel.remove_buildargs(*names)
            self._kernel.send_response(response)

    def _list_argument(self, *names: str):
        """List (specified) *build arguments* of `kernel.DockerKernel`.

        Args:
            *names (tuple[str]): The names of the *build arguments* to be listed.
        """
        buildargs = self._kernel._buildargs
        if len(names) == 0:
            if not buildargs:
                self._kernel.send_response("No current build arguments")
            else:
                self._kernel.send_response("Current build arguments:\n")
                for b in buildargs.keys():
                    self._kernel.send_response(f"\t{b}={buildargs[b]}\n")
        else:
            response = "Current build arguments:\n"
            for name in names:
                if name in buildargs.keys():
                    response = response + f"\t{name}={buildargs[name]}\n"
                else:
                    self._kernel.send_response(
                        f"'{name}' not in current build arguments"
                    )
                    return
            self._kernel.send_response(response)
