from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Type
if TYPE_CHECKING:
    from kernel import DockerKernel

import random
import re
import itertools
from itertools import zip_longest


class MagicError(Exception):
    pass

class Magic(ABC):
    """Abstract class as base for a magic command

    Parameters
    ----------
    kernel: DockerKernel
        Current instance of the Docker kernel
    *args: tuple[str]
        Arguments passed with the magic command
    **flags: dict[str, str]
        Flags passed with the magic command
    """
    def __init__(self, kernel: DockerKernel, *args: str, **flags: str):
        self._kernel = kernel
        self._args = args
        self._find_invalid_args()
        self._shorts, self._flags = Magic._categorize_flags(**flags)
        self._find_invalid_flags()

    @property
    @abstractmethod
    def REQUIRED_ARGS(self) -> tuple[list[str], int]:
        """Defines how many arguments are expected and which are required.

        The returned index is the first thats optional.

        Example
        -------
        (["name", "path", "author"], 1)
        """
        pass
        
    @property
    @abstractmethod
    def ARGS_RULES(self) -> dict[int, list[tuple[Callable[[str], bool], str]]]:
        """Conditions individual arguments must meet.
        NOTE: Conditions based on relations between arguments must be handled inside `_execute_magic()`
        NOTE: Conditions will be checked in order

        The integer key specifies the index of the argument to be checked.
        Indices not present will be ignored.
        The tuple consists of
            - a lambda expression taht returns a bool
            - a description of the condition for an error message

        Example
        -------
        {
            0: [(lambda arg: arg.startswith("%"),
                "Argument must start with a '%'" )],
            2: [(lambda arg: len(re.findall("some regex", arg)) != 0, 
                "Wrong format"),
                (lambda arg: len(re.findall("some regex", arg)) != 0, 
                "Wrong format")]
        }
        """
        pass

    @property
    @abstractmethod
    def VALID_FLAGS(self) -> list[str]:
        """Flags don't won't throw an error

        Example
        -------
        ["image", "path"]
        """
        pass

    @property
    @abstractmethod
    def VALID_SHORTS(self) -> list[str]:
        """Short flags don't won't throw an error

        Example
        -------
        ["i", "p"]
        """
        pass

    @staticmethod
    def detect_magic(code: str):
        """Parse magics, arguments and flags from the cell code.

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
        
        arguments = code.split(" ")
        # Get actual magic name, leaving only the arguments
        magic_name = arguments.pop(0)
        magic_class = Magic._get_magic(magic_name)

        if magic_class is None:
            return None, None, None
        
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

        return magic_class, args, flags

    def call_magic(self) -> list[str]:
        response = self._execute_magic()
        return [response] if type(response) is str else response

    @abstractmethod
    def _execute_magic(self) -> list[str] | str:
        pass

    @staticmethod
    def _get_magic(name: str) -> Type[Magic] | None:
        """ Get Magic specified by name

        Parameters
        ----------
        name: str
            Name of Magic

        Returns
        -------
        Magic | None
        """
        # Magic commands must start with %
        if not name.startswith("%"):
            return None
        
        magics: list[Type[Magic]] = Magic.__subclasses__()
        for magic in magics:
            if magic.__name__.lower() == name.removeprefix("%").lower():
                return magic
        return None

    @staticmethod
    def _categorize_flags(**all_flags: str) -> tuple[dict[str, str], dict[str, str]]:
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
    
    def _find_invalid_args(self):
        """Raise error when current arguments are not valid.

        Raises
        ------
        MagicError
        """
        args, first_optional = self.REQUIRED_ARGS

        for index in range(first_optional):
            try:
                self._args[index]
            except IndexError:
                raise MagicError(f"Missing argument: {args[index]} at position {index+1}")

        for index, rules in self.ARGS_RULES.items():
            try:
                for [rule, message] in rules:
                    if not rule(self._args[index]):
                        raise MagicError(f"Argument at position {index+1} is not valid: {message}")
            except IndexError:
                # Presence of required args already checked
                break

    def _find_invalid_flags(self):
        """Raise error when current flags are not valid

        Raises
        ------
        MagicError
        """
        for flag, value in self._flags.items():
            if flag not in self.VALID_FLAGS:
                raise MagicError(f"Unknown flag: --{flag}")
            if value is None:
                raise MagicError(f"No value for flag: --{flag}")
            
        for short, value in self._shorts.items():
            if short not in self.VALID_SHORTS:
                raise MagicError(f"Unknown shorthand flag: -{short}")
              
            if value is None:
                raise MagicError(f"No value for flag: -{short}")
    
    def _get_default_arg(self, index: int, default: str|None=None):
        """Try to access an arg, return default if not present
        
        Parameters
        ----------
        index: int
            Index of arg
        default: str | None
            Default value

        Returns
        -------
        str | None
        """
        return self._args[index] if -len(self._args) <= index < len(self._args) else default
    
    def _get_default_flag(self, long: str|None=None, short: str|None=None, default: str|None=None):
        """Try to access a flag, return default if not present
        
        Parameters
        ----------
        long: str
            Name of long flag
        long: str
            Name of short flag
        default: str | None
            Default value

        Returns
        -------
        str | None
        """
        return self._flags.get(long, self._flags.get(short, default))


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
