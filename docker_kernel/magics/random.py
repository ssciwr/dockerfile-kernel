from docker_kernel import Magic
from typing import Callable

import random


class Random(Magic):
    """Generate random float between 0 and 1 """
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @property
    def REQUIRED_ARGS(self) -> tuple[list[str], int]:
        return ([], 0)
        
    @property
    def ARGS_RULES(self) -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}
    

    @property
    def VALID_FLAGS(self):
        return []

    @property
    def VALID_SHORTS(self):
        return []
    
    def _execute_magic(self) -> list[str] | str:
        return str(random.random())
