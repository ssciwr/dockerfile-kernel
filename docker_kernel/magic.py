
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Type
if TYPE_CHECKING:
    from .kernel import DockerKernel

from abc import ABC, abstractmethod

import re
import itertools
from itertools import zip_longest

from .magics.helper.errors import MagicError
from .utils.notebook import get_cursor_words, get_cursor_frame, get_first_word
from .magics.helper.types import FlagDict


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

    @staticmethod
    @abstractmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        """Defines how many arguments are expected and which are required.

        The returned index is the first that is optional.

        Example
        -------
        (["name", "path", "author"], 1)
        """
        pass
 
    @staticmethod     
    @abstractmethod
    def ARGS_RULES() -> dict[int, list[tuple[Callable[[str], bool], str]]]:
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

    @staticmethod
    @abstractmethod
    def VALID_OPTIONS() -> list[FlagDict]:
        """ Flags that won't throw an error.
        
        Define their name, shorthand (if available), default value and description

        Example
        -------
        [
            {
                "name": "path",
                "short": "p",
                "default": None,
                "desc": "Path to image"
            },
            {
                "name": "workdir",
                "short": None,
                "default": None,
                "desc": "Directory to execute terminal in"
            }
        ]
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
    
    @classmethod
    @property
    # NOTE: Works, but is supposed to be removed: https://docs.python.org/3.11/library/functions.html#classmethod
    def magics_names(cls) -> list[str]:
        """List all magic names available

        NOTE: The magics must be run once (e.g. via __init__.py) to be listed here

        Returns
        -------
        list[str]
        """
        # Magic commands must start with %
        return [m.__name__.lower() for m in Magic.__subclasses__()]

    @staticmethod
    def do_complete(code: str, cursor_pos: int) -> list[str]:
        segments = code.split(" ")
        first_word = get_first_word(code)
    
        # Code has nothing to do with magics
        if not first_word.startswith("%"):
            return []

        word, _ = get_cursor_words(code, cursor_pos)
        start, _ = get_cursor_frame(code, cursor_pos)

        # Word left of cursor
        partial_word = word[:cursor_pos - start]

        # Cursor on magic name
        if (word == first_word):
            return [f"%{m}" for m in Magic.magics_names if f"%{m}".startswith(partial_word)]
        
        magic = Magic._get_magic(first_word)
        # Magic not known
        if magic is None:
            return []
        
        # Cursor on flag definition
        if word.startswith("-"):
            options = magic.VALID_OPTIONS()
            new_flags = []
            for o in options:
                name = f"--{o['name']}"
                short = f"-{o['short']}" if o['short'] is not None else None
                if name not in segments and short not in segments:
                    new_flags.append(name)
                    if short is not None:
                        new_flags.append(short)
            return [f for f in new_flags if f.startswith(partial_word)]
    
        return []

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
        args, first_optional = self.REQUIRED_ARGS()

        for index in range(first_optional):
            try:
                self._args[index]
            except IndexError:
                raise MagicError(f"Missing argument: {args[index]} at position {index+1}")

        for index, rules in self.ARGS_RULES().items():
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
            if flag not in self.VALID_OPTIONS():
                raise MagicError(f"Unknown flag: --{flag}")
            if value is None:
                raise MagicError(f"No value for flag: --{flag}")
            
        for short, value in self._shorts.items():
            if short not in self.VALID_SHORTS():
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
