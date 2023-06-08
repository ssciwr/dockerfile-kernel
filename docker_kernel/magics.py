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
            # return the image name and tag name
            response = magic_tag(kernel, *args)
        case other:
            response = "Magic not defined"
        
    return [response] if type(response) is str else response


##############################
# Defined Magics

def magic_random():
    return random.random()

def magic_randomInt(stop, start=0, step=1):
    return random.randrange(start, int(stop), step)

def magic_tag(kernel, target):
    DEFAULT_TAG = "latest"
    tags = kernel._tags
    image_id = kernel._sha1

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
