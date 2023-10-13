from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Type

if TYPE_CHECKING:
    from ..kernel import DockerKernel

from abc import ABC, abstractmethod

import re
import itertools
from itertools import zip_longest

from .helper.errors import MagicError
from ..utils.notebook import get_cursor_words, get_cursor_frame, get_first_word
from .helper.types import FlagDict


class Magic(ABC):
    """Abstract class as base for a *Magic* command"""

    def __init__(self, kernel: DockerKernel, *args: str, **flags: str):
        """
        Args:
            kernel (DockerKernel): Current instance of the `DockerKernel`
            *args (tuple[str, ...]): Arguments passed to the *Magic* command
            **flags (tuple[str, ...]): Flags passed to the *Magic* command
        """
        self._kernel = kernel
        self._args = args
        self._find_invalid_args()
        self._shorts, self._flags = Magic._categorize_flags(**flags)
        self._find_invalid_flags()

    @staticmethod
    @abstractmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        """*(abstract, static)* Defines how many arguments are expected and how many of those are required.

        Returns:
            tuple[list[str], int]: A list of accepted arguments and a number that determines the first **optional** argument.
        """
        pass

    @staticmethod
    @abstractmethod
    def ARGS_RULES() -> dict[int, list[tuple[Callable[[str], bool], str]]]:
        """*(abstract, static)* Conditions individual arguments must meet.

        Returns:
            dict[int, list[tuple[Callable[[str], bool], str]]]: Dictionary assigning a list of conditions and corresponding error message to an argument.
                The argument is specified by its index in the `REQUIRED_ARGS` list.
        """
        pass

    @staticmethod
    @abstractmethod
    def VALID_FLAGS() -> dict[str, FlagDict]:
        """*(abstract, static)* Flags that are accepted by the *Magic*.

        Returns:
            dict[str, FlagDict]: Assigns each flag a `FlagDict`
        """
        pass

    @staticmethod
    def detect_magic(code: str):
        """*(static)* Parse *Magics*, *arguments* and *flags* from the cell code.

        Args:
            code (str): The user's code.

        Returns:
            tuple(Magic, tuple[str], dict[str, str]) | tuple(None, None, None): The *Magic* found in the code with all its *args* and *flags* as well as the flags values.
                Or `None` for all if no *Magic* was found.
        """
        # Remove multi-/ trailing / leading spaces
        code = re.sub(" +", " ", code).strip()

        arguments = code.split(" ")
        # Get actual magic name, leaving only the arguments
        magic_name = arguments.pop(0)
        magic_class = Magic._get_magic(magic_name)

        if magic_class is None:
            return None, None, None

        # Separate args and flags
        args: tuple[str] = ()
        flags: dict[str, str] = {}
        c, n = itertools.tee(arguments)
        next(n, None)  # two iterators with one ahead of the other
        it = iter(zip_longest(c, n))
        for arg, narg in it:
            if arg.startswith("-") and len(arg) >= 2:
                flags[arg] = narg
                next(it, None)
            else:
                args = args + (arg,)

        return magic_class, args, flags

    def call_magic(self) -> None:
        """Call the magic's logic itself."""
        self._execute_magic()

    @abstractmethod
    def _execute_magic(self) -> None:
        """*(abstract)* Execute the magic's logic."""
        pass

    @staticmethod
    def _get_magic(name: str) -> Type[Magic] | None:
        """*(static)* Get *Magic* via its name.

        Args:
            name (str): Name of the *Magic*.

        Raises:
            MagicError: No *Magic* found for *name*.

        Returns:
            Type[Magic] | None: *Magic* found for *name*. Or `None` if potential name didn't start with a %.
        """
        # Magic commands must start with %
        if not name.startswith("%"):
            return None

        magics: list[Type[Magic]] = Magic.__subclasses__()
        for magic in magics:
            if magic.__name__.lower() == name.removeprefix("%").lower():
                return magic

        # No magic found but indicated by leading %
        raise MagicError(f"No magic named {name.removeprefix('%')}")

    @classmethod
    @property
    # NOTE: Classmethod wrapping works, but is supposed to be removed: https://docs.python.org/3.11/library/functions.html#classmethod
    def magics_names(cls) -> list[str]:
        """*(classmethod)* List names of all *Magics* available.

        Returns:
            list[str]: Names of all *Magics* available.
        """
        return [m.__name__.lower() for m in Magic.__subclasses__()]

    @staticmethod
    def do_complete(code: str, cursor_pos: int) -> list[str]:
        """*(static)* Provide *Magic* specific code completion for the `kernel.do_complete` method.

        Args:
            code (str): The user's code.
            cursor_pos (int): The cursor's position in *code*. This is where the completion is requested.

        Returns:
            list[str]: Code completion words and phrases.
        """
        segments = code.split(" ")
        first_word = get_first_word(code)

        # Code has nothing to do with magics
        if not first_word.startswith("%"):
            return []

        word, _ = get_cursor_words(code, cursor_pos)
        start, _ = get_cursor_frame(code, cursor_pos)

        # Word left of cursor
        partial_word = word[: cursor_pos - start]

        # Cursor on magic name
        if word == first_word:
            return [
                f"%{m}" for m in Magic.magics_names if f"%{m}".startswith(partial_word)
            ]

        magic = Magic._get_magic(first_word)
        # Magic not known
        if magic is None:
            return []

        # Cursor on flag definition
        if word.startswith("-"):
            options: dict[str, FlagDict] = magic.VALID_FLAGS()
            new_flags = []
            for name, details in options.items():
                name = f"--{name}"
                short = f"-{details['short']}" if details["short"] is not None else None
                if name not in segments and short not in segments:
                    new_flags.append(name)
                    if short is not None:
                        new_flags.append(short)
            return [f for f in new_flags if f.startswith(partial_word)]

        return []

    @staticmethod
    def _categorize_flags(**all_flags: str) -> tuple[dict[str, str], dict[str, str]]:
        """*(static)* Separate *shorthand flags* and normal *flags*.

        Returns:
            tuple[dict[str, str], dict[str, str]]: The *shorthand flags* and normal *flags* used as well as wach of their values.
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
        """Raise error when current *arguments* are not valid.

        Raises:
            MagicError: Required *argument* is missing.
            MagicError: An *argument's* value isn't valid
        """
        args, first_optional = self.REQUIRED_ARGS()

        for index in range(first_optional):
            try:
                self._args[index]
            except IndexError:
                raise MagicError(
                    f"Missing argument: {args[index]} at position {index+1}"
                )

        for index, rules in self.ARGS_RULES().items():
            try:
                for [rule, message] in rules:
                    if not rule(self._args[index]):
                        raise MagicError(
                            f"Argument at position {index+1} is not valid: {message}"
                        )
            except IndexError:
                # Presence of required args already checked
                break
        if args == [] and self._args:
            raise MagicError(f"No argument is needed")

    def _find_invalid_flags(self):
        """Raise error when a *flag* is not valid.

        Raises:
            MagicError: The *flag* is not known.
            MagicError: No value was given for *flag*.
            MagicError: The *shorthand flag* is not known.
            MagicError: No vlaue was given for *shorthand flag*.
            MagicError: Both *flag* and *shorthand flag* were passed.
        """
        options: dict[str, FlagDict] = self.VALID_FLAGS()
        flags = list(options.keys())
        shorts = [d["short"] for d in options.values() if d["short"] is not None]
        for flag, value in self._flags.items():
            if flag not in flags:
                raise MagicError(f"Unknown flag: --{flag}")
            if value is None:
                raise MagicError(f"No value for flag: --{flag}")

        for short, value in self._shorts.items():
            if short not in shorts:
                raise MagicError(f"Unknown shorthand flag: -{short}")

            if value is None:
                raise MagicError(f"No value for flag: -{short}")

        for flag, detail in options.items():
            if flag in self._flags.keys() and detail["short"] in self._shorts.keys():
                raise MagicError(f"Duplicate flag: -{short} and --{flag}")

    def _get_default_arg(self, index: int, default: str | None = None):
        """Get an *argument* by its index or return a default.

        Args:
            index (int): Index of the *argument*.
            default (str | None, optional): Default if index no *argument* at index.
                Defaults to None.

        Returns:
            str: Value of *argument* or default.
        """
        return (
            self._args[index]
            if -len(self._args) <= index < len(self._args)
            else default
        )

    def _get_default_flag(
        self,
        long: str | None = None,
        short: str | None = None,
        default: str | None = None,
    ):
        """Try to access a *flag* or return a default.

        Args:
            long (str | None, optional): Normal *flag* name.
                Defaults to None.
            short (str | None, optional): *Shorthand flag* name.
                Defaults to None.
            default (str | None, optional): Default if neither *shorthand flag* nor *flag* is found.
                Defaults to None.

        Returns:
            str: Value of *flag* or default.
        """
        return self._flags.get(long, self._flags.get(short, default))
