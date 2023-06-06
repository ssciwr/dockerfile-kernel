import random

def detect_magic(code: str):
    """Parse magics from the cell code.

    Parameters
    ----------
    code: str
        Cell input

    Returns
    -------
    magic: str | None
    arguments: list[str]
    """
    code = code.lstrip()
    magic_present = code.startswith("%")
    if not magic_present:
        return None, []
    
    arguments = code.split(" ")
    # get actual magic command, leaving only the arguments
    magic = arguments.pop(0)[1:]
    return magic, arguments

def call_magic(kernel, magic: str, args: list[str]):
    """Determine if a magic command is known. If so, return its function.

    Parameters
    ---------_
    magic: str
        Magic command

    Returns
    -------
    reponse: str
    """
    match magic.lower():
        case "random":
            return str(magic_random(*args))
        case "randint":
            return str(magic_randomInt(*args))
        case "install":
            return str(magic_install(kernel, *args))
        case other:
            return "Magic not defined"


##############################
# Defined Magics

def magic_random():
    return random.random()

def magic_randomInt(stop, start=0, step=1):
    return random.randrange(start, int(stop), step)

def magic_install(kernel, *args):
    match args[0].lower():
        case "apt-get":
            package = str(args[1:]) 
            code = f"CMD apt-get update && apt-get install -y {package} && rm-rf /var/lib/apt/lists/*"
        case other:
            return "Package manager not available (currently available: apt-get)"
    code = kernel.create_build_stage(code)
    return "\n".join(kernel.build_image(code))
