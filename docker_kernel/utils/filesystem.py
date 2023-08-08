import os
import tempfile
import shutil

def create_dockerfile(code: str, directory: str, filename="Dockerfile"):
    dockerfile_path = os.path.join(directory, filename)
    with open(dockerfile_path, 'w+') as dockerfile:
        dockerfile.write(code)
    return dockerfile_path


def copy_files(src: str, dest: str):
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
    except shutil.Error as e:
        self.send_response(str(e))
def remove_tmp_dir(tmp_dir: tempfile.TemporaryDirectory):
    try:
        tmp_dir.cleanup()
    except Exception as e:
        self.send_response(str(e))
