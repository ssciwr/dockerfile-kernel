from typing import Callable

from .magic import Magic
from .helper.types import FlagDict


class Install(Magic):
    """Install additional packages to the docker image."""
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["package-manager", "package"], 2)
        
    @staticmethod
    def ARGS_RULES() -> dict[int, tuple[Callable[[str], bool], str]]:
        return {}
    
    @staticmethod
    def VALID_OPTIONS() -> dict[str, FlagDict]:
        return {}
    
    def _execute_magic(self) -> list[str] | str:
        package = " ".join(self._args[1:])
        match self._args[0].lower():
            case "apt-get":
                code = f"RUN apt-get update && apt-get install -y**PACKAGES**{package}**PACKAGES**&& rm -rf /var/lib/apt/lists/*"
            case "conda":
                code = f"RUN conda update -n base -c defaults conda && conda install -y**PACKAGES**{package}**PACKAGES**&& conda clean -afy"
            case "npm":
                code = f"RUN npm install -g npm@latest && npm install**PACKAGES**{package}**PACKAGES**&& npm cache clean --force"
            case "pip":
                code = f"RUN pip install --upgrade pip && pip install**PACKAGES**{package}**PACKAGES**&& rm -rf /var/lib/apt/lists/*"
            case other:
                return "Package manager not available (currently available: apt-get)"
        self._kernel.set_payload("set_next_input", self._set_layout(code, "\n"), True)
        code = self._kernel.create_build_stage(self._set_layout(code, "\\"))
        self._kernel.build_image(code)

    def _set_layout(self, code: str, newline_character: str) -> str:
        code = code.split("**PACKAGES**")
        code[1] = code[1].replace(" ", f"{newline_character}\t")
        code = " ".join(code)
        code = code.replace("&&", f"&&{newline_character}")
        return code
