from typing import Callable

import os

from .magic import Magic
from .helper.types import FlagDict


class Context(Magic):
    """Change the directory used as *build context* by `kernel.DockerKernel`."""

    def __init__(self, kernel, *args, **flags):
        super().__init__(kernel, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["directory_path"], 1)

    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        exists: Callable[[str], bool] = lambda path: os.path.exists(path)
        is_directory: Callable[[str], bool] = lambda path: os.path.isdir(path)
        return {
            0: [
                (exists, "Specified directory doesn't exist"),
                (is_directory, "Specified path is no directory"),
            ]
        }

    @staticmethod
    def VALID_FLAGS() -> dict[str, FlagDict]:
        return {}

    def _execute_magic(self) -> None:
        directory_path = self._args[0]
        self._kernel.change_build_context_directory(directory_path)
