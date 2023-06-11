from .kernel import DockerKernel, __version__
from .magic import Magic

# Run code of all magics to make them accessabble to Magic.__subclasses()
import os
for magic in os.scandir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "magics")):
    if magic.is_file():
        if not magic.name.endswith(".py"):
            continue
        if magic.name.startswith ("__"):
            continue
        string = f"from .magics import {magic.name.removesuffix('.py')}"
        exec (string)