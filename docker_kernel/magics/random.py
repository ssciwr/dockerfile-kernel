from docker_kernel import Magic
from typing import Callable

import random


class Random(Magic):
    """Generate random float between 0 and 1 """
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return ([], 0)
        
    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}
    

    @staticmethod
    def VALID_FLAGS():
        return []

    @staticmethod
    def VALID_SHORTS():
        return []
    
    def _execute_magic(self) -> list[str] | str:
        return str(random.random())
