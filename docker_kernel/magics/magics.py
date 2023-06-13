from typing import Callable

from docker_kernel.magic import Magic
from .helper.types import FlagDict


class Magics(Magic):
    """List all available magics """
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return ([], 0)
        
    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}
    
    @staticmethod
    def VALID_OPTIONS() -> dict[str, FlagDict]:
        return {}
    
    def _execute_magic(self) -> None:
        magics = self.magics_names
        magics.sort()
        self._kernel.send_response("\n".join(magics))
