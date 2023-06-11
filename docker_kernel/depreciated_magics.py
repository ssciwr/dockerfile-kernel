from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kernel import DockerKernel

#! DEPRECTIATED
#TODO: Implement Install magic as Magic Object
def magic_install(kernel: DockerKernel, *args: str, **flags: str):
    """ Install additional packages to the docker image.

    Parameters
    ----------
    kernel: DockerKernel
        Kernel instance
    args: tuple[str]
        install arguments, e.g. package manager, packages
    flags: dict[str, str]
        install flags, currently not used

    Returns
    -------
    list[str]
    """
    match args[0].lower():
        case "apt-get":
            package = " ".join(args[1:])
            code = f"RUN apt-get update && apt-get install -y {package} && rm -rf /var/lib/apt/lists/*"
        case other:
            return "Package manager not available (currently available: apt-get)"
    kernel.set_payload("set_next_input", code, True)
    code = kernel.create_build_stage(code)
    return kernel.build_image(code)



