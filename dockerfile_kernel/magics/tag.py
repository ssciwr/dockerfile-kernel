from typing import Callable

import docker.client

from .magic import Magic
from .helper.errors import MagicError
from .helper.types import FlagDict


class Tag(Magic):
    """Save Docker image with a name and tag in the `kernel.DockerKernel`."""

    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["target image"], 1)

    @staticmethod
    def ARGS_RULES() -> dict[int, list[tuple[Callable[[str], bool], str]]]:
        return {
            0: [
                (
                    lambda arg: not arg.startswith(":"),
                    "Image name can't start with a ':'",
                ),
                (lambda arg: arg.count(":") <= 1, "Tag can't contain ':'"),
                (lambda arg: not arg.endswith(":"), "Image name can't end in a ':'"),
            ],
        }

    @staticmethod
    def VALID_FLAGS() -> dict[str, FlagDict]:
        return {"image": {"short": "i", "default": None, "desc": "Image to be tagged"}}

    def _execute_magic(self) -> None:
        target_image = self._args[0]
        try:
            name, tag = target_image.split(":")
        except ValueError as e:
            # If no colon is provided the default tag is used
            if ":" not in target_image:
                name = target_image
                tag = None
            else:
                raise MagicError(
                    "Error parsing arguments:\n"
                    + f'\t"{target_image}" is not valid: Invalid reference format'
                )

        self._kernel.tag_image(name, tag=tag)
