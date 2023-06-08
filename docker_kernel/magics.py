import random

def detect_magic(code: str):
    """Parse magics from the cell code.

    Parameters
    ----------
    code: str
        Cell input

    Returns
    -------
    tuple(magic: str | None, arguments: tuple[str] | None)
    """
    code = code.strip()
    magic_present = code.startswith("%")
    
    if not magic_present:
        return None, None
    
    arguments = code.split(" ")
    # get actual magic command, leaving only the arguments
    magic = arguments.pop(0)[1:]


    for index, argument in enumerate(arguments):
        if ":" in argument:
            sub_args = argument.split(":")
            arguments.pop(index)
            # i = 0
            for idx, sub_arg in enumerate(sub_args):
                arguments.insert(index+idx, sub_arg)
                # i = i + 1

    return magic, tuple(arguments)

def call_magic(magic: str, *args: str):
    """Determine if a magic command is known. If so, execute it and return its response.

    Parameters
    ----------
    magic: str
        Magic command
    args: tuple[str]
        Magic arguments

    Returns
    -------
    reponse: list[str]
    """
    match magic.lower():
        case "random":
            float = magic_random()
            return [str(float)]
        case "randint":
            int = magic_randomInt(*args)
            return [str(int)]
        case "tag":
            # return the image name and tag name
            return str(magic_tag(args))
        case other:
            return ["Magic not defined"]


##############################
# Defined Magics

def magic_random():
    return random.random()

def magic_randomInt(stop, start=0, step=1):
    return random.randrange(start, int(stop), step)

def magic_tag(args):
    # get the image name and tag name
    return args[0:2]
