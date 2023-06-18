from typing import Callable

from .magic import Magic
from .helper.errors import MagicError
from.helper.types import FlagDict

class Tag(Magic):
    """Save a docker image via a name and tag in the kernel for later access."""
    def __init__(self, kernle, *args, **flags):
        super().__init__(kernle, *args, **flags)

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        return (["target"], 1)
        
    @staticmethod
    def ARGS_RULES() -> dict[int, list[tuple[Callable[[str], bool], str]]]:
        return {
            0: [(lambda arg: not arg.startswith(":"),
                 "Image name can't start with a ':'"),
                 (lambda arg: arg.count(":") <=1,
                  "Tag can't contain ':'"),
                  (lambda arg: not arg.endswith(":"),
                   "Image name can't end in a ':'")],
        }

    @staticmethod
    def VALID_OPTIONS() -> dict[str, FlagDict]:
        return {
            "image" : {
                "short": "i",
                "default": None,
                "desc": "Image to be tagged"
            }
        }
    
    def _execute_magic(self) -> None:
        target = self._args[0]
        try:
            name, tag = target.split(":")
        except ValueError as e:
            # If no colon is provided the default tag is used
            if ":" not in target:
                name = target
                tag = None
            else:
                raise MagicError("Error parsing arguments:\n" + 
                                f"\t\"{target}\" is not valid: invalid reference format")

        image_id = self._get_default_flag("image", "i", self._kernel._sha1)
        if image_id is None:
            raise MagicError("No image specified")

        self._kernel.tag_image(image_id, name, tag=tag)

        image_str = image_id.removeprefix("sha256:")
        image_str = f"{image_str[:10]}..." if len(image_str) >= 10 else image_str
        self._kernel.send_response(f"Image {image_str} tagged")
