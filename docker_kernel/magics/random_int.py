from typing import Callable

import random

from docker_kernel.magic import Magic
from docker_kernel.utils.conversion import try_convert
from .helper.errors import MagicError
from .helper.types import FlagDict


class RandomInt(Magic):
    """Generate random integer between two given integers"""
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["stop", "start", "step"], 1)
        
    @staticmethod
    def ARGS_RULES() -> dict[int, list[tuple[Callable[[str], bool], str]]]:
        is_positive_integer: Callable[[str], bool] = lambda arg: try_convert(arg, None, int) is not None
        return {
            0: [(is_positive_integer,
                 "Stop must be a positive integer")],
            1: [(is_positive_integer,
                 "Start must be a positive integer")],
            2: [(is_positive_integer,
                 "Step must be a positive integer")]
        }

    @staticmethod
    def VALID_OPTIONS() -> list[FlagDict]:
        return []
    
    def _execute_magic(self) -> None:
        stop = int(self._args[0])
        start = self._get_default_arg(1, 0)
        step = self._get_default_arg(2, 1)

        if start >= stop:
            raise MagicError("Empty range: start must be smaller than stop")

        r = random.randrange(start, stop, step)
        self._kernel.send_response(str(r))
