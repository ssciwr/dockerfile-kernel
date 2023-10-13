import os
import shutil
from typing import Callable, Iterable


def create_dockerfile(code: str, directory: str):
    """Create a *Dockerfile*

    Args:
        code (str): The *Dockerfile* code.
        directory (str): Path to create *Dockerfiel* in.
        filename (str, optional): Filename of *Dockerfile*.
            Defaults to "Dockerfile".

    Returns:
        str: Path of the created *Dockerfile*
    """
    dockerfile_path = os.path.join(directory, "Dockerfile")
    with open(dockerfile_path, "w+") as dockerfile:
        dockerfile.write(code)
    return dockerfile_path


def copy_files(
    src: str, dest: str, ignore: Callable[[str, list[str]], Iterable[str]] | None = None
):
    """Copy files from one directory to another.

    Args:
        src (str): Path of source directory.
        dest (str): Path of destination directory.
        ignore (Callable[[str, list[str]], Iterable[str]] | None, optional): Ignore callable for [shutil.copytree](https://docs.python.org/3/library/shutil.html#shutil.copytree)
            Defaults to None.

    Returns:
        bool | Error : Returns `True` if copying was successfull, else an Error.
    """
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True, ignore=ignore)
        return True
    except shutil.Error as e:
        return e


def empty_dir(dir_path: str):
    """Empty a given directory without deleting the directory itself.

    Args:
        dir_path (str): Path of directory to be emtied.

    Returns:
        bool | Error : Returns `True` if emptying was successfull, else an Error.
    """
    try:
        contents = os.listdir(dir_path)
        for item in contents:
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        return True
    except FileNotFoundError as e:
        return e


def get_dir_size(
    start_path: str, ignore: Callable[[str, list[str]], Iterable[str]] = None
):
    """Get directoy size in bytes

    Args:
        start_path (str): Path of the directory.
        ignore (Callable[[str, list[str]], Iterable[str]] | None, optional), optional): Callable that determines what files are not to be included in calculation.
            See [ignore of shutil.copytree](https://docs.python.org/3/library/shutil.html#shutil.copytree) for reference.
            Defaults to None.

    Returns:
        _type_: _description_
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        ignore_files = []
        if ignore:
            ignore_files = ignore(dirpath, filenames)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp) and f not in ignore_files:
                total_size += os.path.getsize(fp)

    return total_size
