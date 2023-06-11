from docker_kernel.magic import Magic
from typing import Callable
from .errors import MagicError

import random

from docker_kernel.utils.conversion import try_convert


class RandomInt(Magic):
    """Generate random integer between two given integers"""
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @property
    def REQUIRED_ARGS(self) -> tuple[list[str], int]:
        return (["stop", "start", "step"], 1)
        
    @property
    def ARGS_RULES(self) -> dict[int, list[tuple[Callable[[str], bool], str]]]:
        is_positive_integer: Callable[[str], bool] = lambda arg: try_convert(arg, None, int) is not None
        return {
            0: [(is_positive_integer,
                 "Stop must be a positive integer")],
            1: [(is_positive_integer,
                 "Start must be a positive integer")],
            2: [(is_positive_integer,
                 "Step must be a positive integer")]
        }

    @property
    def VALID_FLAGS(self):
        return []

    @property
    def VALID_SHORTS(self):
        return []
    
    def _execute_magic(self) -> list[str] | str:
        stop = int(self._args[0])
        start = self._get_default_arg(1, 0)
        step = self._get_default_arg(2, 1)

        if start >= stop:
            raise MagicError("Empty range: start must be smaller than stop")

        return str(random.randrange(start, stop, step))
