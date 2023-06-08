import random

def detect_magic(code: str):
    """Parse magics from the cell code.

    Parameters
    ----------
    code: str
        Cell input

    Returns
    -------
    tuple(str | None, tuple[str] | None)
        Name of the magic and passed arguments.

        Null for both if magic not known.
    """
    code = code.strip()
    magic_present = code.startswith("%")
    
    if not magic_present:
        return None, None
    
    arguments = code.split(" ")
    # get actual magic command, leaving only the arguments
    magic = arguments.pop(0)[1:]

    return magic, tuple(arguments)

def call_magic(kernel, magic: str, *args: str):
    """Determine if a magic command is known. If so, execute it and return its response.

    Parameters
    ----------
    kernel: DockerKernel
        Current instance of the docker kernel
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
            response = str(float)
        case "randint":
            int = magic_randomInt(*args)
            response = str(int)
        case "tag":
            response = magic_tag(kernel, *args)
        case other:
            response = "Magic not defined"
        
    return [response] if type(response) is str else response


##############################
# Defined Magics

def magic_random():
    """Generate random float between 0 and 1

    Returns
    -------
    random: int
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

def magic_tag(kernel, target):
    """Save a docker image via a name and tag in the kernel for later access.

    Parameters
    ----------
    kernel: DockerKernel
        Kernel instance
    target: str
        Name and tag thats being assigned to the image.
        
        If no tag is passed, a default is used.

        Format: "name:tag"
    
    Returns
    -------
    str
        Message to be printed in the notebook
    """
    DEFAULT_TAG = "latest"
    tags = kernel._tags
    image_id = kernel._sha

    if image_id is None:
        return "Error storing image: No image found"

    try:
        name, tag = target.split(":")
    except ValueError as e:
        # If no colon is provided the default tag is used
        if ":" not in target:
            name = target
            tag = DEFAULT_TAG
        else:
            return [f"Error parsing arguments:",
                    f"\t\"{target}\" is not valid: invalid reference format"]

    if name not in tags:
        tags[name] = {}

    save_type = "stored" if tags[name].get(tag, None) is None else "overwritten"
    tags[name][tag] = image_id
    return [f"The image with id {image_id} was {save_type}:", 
            f"name: {name}",
            f"tag: {tag}"]
