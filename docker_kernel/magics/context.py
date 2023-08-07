from typing import Callable

import os

from .magic import Magic
from .helper.types import FlagDict


class Context(Magic):
    """Change the directory used as a building context """
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["directory_path"], 1)
        
    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        exists: Callable[[str], bool] = lambda path: os.path.exists(path)
        is_directory: Callable[[str], bool] = lambda path: os.path.isdir(path)
        return {
            0: [(exists, "Specified directory doesn't extist"),
                (is_directory, "Specified path is no directory")]
        }
    
    @staticmethod
    def VALID_OPTIONS() -> dict[str, FlagDict]:
        return {}
    
    def _execute_magic(self) -> None:
        directory_path = self._args[0]
        self._kernel.change_build_context_directory(directory_path)
