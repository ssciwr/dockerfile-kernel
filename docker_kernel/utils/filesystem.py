import os
import shutil

def create_dockerfile(code: str, directory: str, filename="Dockerfile"):
    """Create a *Dockerfile*
    
    #TODO: Remove filename (not used)

    Args:
        code (str): The *Dockerfile* code.
        directory (str): Path to create *Dockerfiel* in.
        filename (str, optional): Filename of *Dockerfile*.
            Defaults to "Dockerfile".

    Returns:
        str: Path of the created *Dockerfile*
    """
    dockerfile_path = os.path.join(directory, filename)
    with open(dockerfile_path, 'w+') as dockerfile:
        dockerfile.write(code)
    return dockerfile_path

def copy_files(src: str, dest: str):
    """Copy files from one directory to another.

    Args:
        src (str): Path of source directory.
        dest (str): Path of destination directory.

    #TODO: Don't return error, only message. Or figure out something better
        
    Returns:
        bool | Error : Returns `True` if copying was successfull, else an Error.
    """
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
        return True
    except shutil.Error as e:
        return e

def empty_dir(dir_path: str):
    """Empty a given directory without deleting the directory itself.

    Args:
        dir_path (str): Path of directory to be emtied.

    #TODO: Don't return error, only message. Or figure out something better

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
