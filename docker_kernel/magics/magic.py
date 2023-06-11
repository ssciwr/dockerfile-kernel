from docker_kernel.magic import Magic as BaseMagic
from typing import Callable


class Magic(BaseMagic):
    """List all available magics """
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
        return [m.__name__.lower() for m in BaseMagic.__subclasses__()]
