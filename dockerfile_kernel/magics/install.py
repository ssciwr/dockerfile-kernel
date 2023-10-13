from typing import Callable, Tuple

from .magic import Magic
from .helper.types import FlagDict


class Install(Magic):
    """Install additional packages to the Docker image."""

    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["package-manager", "package"], 2)

    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}

    @staticmethod
    def VALID_FLAGS() -> dict[str, FlagDict]:
        return {}

    def _execute_magic(self) -> list[str] | str:
        code = None
        packages = " {newLine}".join(self._args[1:])
        match self._args[0].lower():
            case "apt-get" | "apt":
                code = (
                    "RUN apt-get update {newLine}apt-get install -y "
                    + f"{packages}"
                    + " {newLine}rm -rf /var/lib/apt/lists/*"
                )
            case "conda":
                code = (
                    "RUN conda install -y --freeze-installed "
                    + f"{packages}"
                    + " {newLine}conda clean -afy"
                )
            case "conda-forge":
                code = (
                    "RUN conda install -y --freeze-installed -c conda-forge"
                    + f"{packages}"
                    + " {newLine}conda clean -afy"
                )
            case "npm":
                code = (
                    "RUN npm install "
                    + f"{packages}"
                    + " {newLine}npm cache clean --force"
                )
            case "pip":
                code = (
                    "RUN pip install --upgrade pip {newLine}pip install "
                    + f"{packages}"
                    + " {newLine}rm -rf /root/.cache/pip"
                )
            case other:
                self._kernel.send_response(
                    "Package manager not available (currently available: apt(-get), conda, conda-forge, npm, pip)"
                )

        if code is not None:
            self._kernel.payload = (
                "set_next_input",
                code.format(newLine="&&\\\n\t "),
                True,
            )
            code = self._kernel.create_build_stage(code.format(newLine="&& "))
            self._kernel.build_image(code)
