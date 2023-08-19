import os
import shutil
from typing import Callable, Iterable

def create_dockerfile(code: str, directory: str, filename="Dockerfile"):
    dockerfile_path = os.path.join(directory, filename)
    with open(dockerfile_path, 'w+') as dockerfile:
        dockerfile.write(code)
    return dockerfile_path

def copy_files(src: str, dest: str, ignore: Callable[[str, list[str]], Iterable[str]] | None = None):
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True, ignore=ignore)
        return True
    except shutil.Error as e:
        return e

def empty_dir(dir_path: str):
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
