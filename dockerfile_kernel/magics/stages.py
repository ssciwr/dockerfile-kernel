from .magic import Magic
from typing import Callable
from .helper.types import FlagDict


class Stages(Magic):
    """
    list all the stages
    """

    def __int__(self, kernel, *args, **flags):
        super().__int__(kernel, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return ([], 0)

    @staticmethod
    def ARGS_RULES() -> dict[int, list[tuple[Callable[[str], bool], str]]]:
        return {}

    @staticmethod
    def VALID_FLAGS() -> dict[str, FlagDict]:
        return {}

    def _execute_magic(self) -> None:
        stages_table = self._kernel.get_stages()
        self._kernel.send_response(f"{stages_table}\n")
