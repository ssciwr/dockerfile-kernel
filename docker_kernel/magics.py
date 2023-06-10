from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kernel import DockerKernel

import random
import re
import itertools
from itertools import zip_longest

def detect_magic(code: str):
    """Parse magics from the cell code.

    Parameters
    ----------
    code: str
        Cell input

    Returns
    -------
    tuple(str | None, tuple[str] | None, dict[str, str] | None)
        Name of the magic, args and flags.
        In kwargs: Normal flags start with a hyphen, shorthand flags omit it.

        Null for all if magic not known.
    """
    # Remove multi-/ trailing / leading spaces
    code = re.sub(' +', ' ', code).strip()
    magic_present = code.startswith("%")
    
    if not magic_present:
        return None, None, None
    
    arguments = code.split(" ")
    # Get actual magic command, leaving only the arguments
    magic = arguments.pop(0)[1:]
    
    # Separate args and flags
    args = ()
    flags = {}
    c, n = itertools.tee(arguments)
    next(n, None) # two iterators with one ahead of the other
    it = iter(zip_longest(c, n))
    for arg, narg in it:
        if arg.startswith("-") and len(arg) >= 2:
            flags[arg] = narg
            next(it, None)
        else:
            args = args + (arg,)
    return magic, args, flags

def call_magic(kernel: DockerKernel, magic: str, *args: str, **flags: str):
    """Determine if a magic command is known. If so, execute it and return its response.

    Parameters
    ----------
    kernel: DockerKernel
        Current instance of the docker kernel
    magic: str
        Magic command
    args: tuple[str]
        Magic arguments
    flags: dict[str, str]
        Magic flags

    Returns
    -------
    reponse: list[str]
    """
    match magic.lower():
        case "magic":
            response = magic_magic()
        case "random":
            float = magic_random()
            response = str(float)
        case "randint":
            int = magic_randomInt(*args)
            response = str(int)
        case "install":
            response = magic_install(kernel, *args)    
        case "tag":
            response = magic_tag(kernel, *args, **flags)
        case other:
            response = "Magic not defined"
            
    return [response] if type(response) is str else response

def categorize_flags(**all_flags: str):
    """Separates shorthand flags from normal flags

    Parameters
    ----------
    flags: dict[str, str]

    Returns
    -------
    tuple[shorts: dict[str, str], flags: dict[str, str]]
    """
    flags: dict[str, str] = {}
    shorts: dict[str, str] = {}
    for flag, option in all_flags.items():
        if flag.startswith("--"):
            flags[flag[2:]] = option
        else:
            shorts[flag[1:]] = option
    return shorts, flags


##############################
# Defined Magics

DEFINED_MAGICS = ["install", "magic", "random", "randomInt", "tag"]
DEFINED_MAGICS.sort()

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

def magic_magic():
    """ List all available magic commands.

    Returns
    -------
    list[str]
        Available magics.
    """
    return [f"%{magic}" for magic in DEFINED_MAGICS]

def magic_random():
    """ Generate random float between 0 and 1

    Returns
    -------
    int
    """
    return random.random()

def magic_randomInt(stop: int, start=0, step=1):
    """Generate random integer between two given integers

    Parameters
    ----------
    stop: int
        Max value (not included)
    start: int, optional
        Min value (included)
    step: int, optional
        Incrementation
    
    Returns
    -------
    int
        Generated integer
    """
    return random.randrange(start, int(stop), step)

def magic_tag(kernel: DockerKernel, target: str, **flags: str):
    """Save a docker image via a name and tag in the kernel for later access.

    Parameters
    ----------
    kernel: DockerKernel
        Kernel instance
    target: str
        Name and tag that are being assigned to the image.
        
        If no tag is passed, a default is used.

        Format: "name:tag"
    image: str | None, optional
        Specific image id. 
    
    Returns
    -------
    str
        Message to be printed in the notebook
    """
    ALLOWED_FLAGS = ["image"]
    ALLOWED_SHORTS = ["i"]

    shorts, flags = categorize_flags(**flags)

    # Find invalid flags
    for flag in flags.keys():
        if flag not in ALLOWED_FLAGS:
            return [f"Unknown flag: --{flag}"]
    for short in shorts.keys():
        if short not in ALLOWED_SHORTS:
            return [f"Unknown shorthand flag: -{short}"]

    try:
        name, tag = target.split(":")
    except ValueError as e:
        # If no colon is provided the default tag is used
        if ":" not in target:
            name = target
            tag = None
        else:
            return [f"Error parsing arguments:",
                    f"\t\"{target}\" is not valid: invalid reference format"]
        
    image_id = shorts.get("i", flags.get("image"))

    kernel.tag_image(name, tag=tag, image_id=image_id)

    return []
