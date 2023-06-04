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
    """
    magic_present = code.lstrip().startswith("%")
    if not magic_present:
        return None
    # discard everything after the detected magic as well as the leading "%"
    return code.lstrip().split(" ")[0][1:]

def call_magic(magic: str):
    """Determine if a magic command is known. If so, return its function.

    Parameters
    ---------_
    magic: str
        Magic command

    Returns
    -------
    reponse: str
    """
    match magic:
        case "random":
            return str(magic_random())
        case other:
            return "Magic not defined"


##############################
# Defined Magics

def magic_random():
    return random.random()