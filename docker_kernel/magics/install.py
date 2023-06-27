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
        packagesPayload = "\n\t".join(self._args[1:])
        packagesDocker = " ".join(self._args[1:])
        match self._args[0].lower():
            case "apt-get" | "apt" :
                code = f"RUN apt-get update && apt-get install -y {packagesDocker} && rm -rf /var/lib/apt/lists/*"
                payload = f"RUN apt-get update && apt-get install -y {packagesPayload} && rm -rf /var/lib/apt/lists/*"
            case "conda":
                code = f"RUN conda update -n base -c defaults conda && conda install -y {packagesDocker} && conda clean -afy"
                payload = f"RUN conda update -n base -c defaults conda && conda install -y {packagesPayload} && conda clean -afy"
            case "npm":
                code = f"RUN npm install -g npm@latest && npm install {packagesDocker} && npm cache clean --force"
                payload = f"RUN npm install -g npm@latest && npm install {packagesPayload} && npm cache clean --force"
            case "pip":
                code = f"RUN pip install --upgrade pip && pip install {packagesDocker} && rm -rf /var/lib/apt/lists/*"
                payload = f"RUN pip install --upgrade pip && pip install {packagesPayload} && rm -rf /var/lib/apt/lists/*"
            case other:
                return "Package manager not available (currently available: apt(-get), conda, npm, pip)"
        self._kernel.set_payload("set_next_input", payload.replace("&&", "&&\n\t") ,True)
        code = self._kernel.create_build_stage(code)
        self._kernel.build_image(code)