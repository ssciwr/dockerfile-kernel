import os

def create_dockerfile(code: str, directory: str, filename="Dockerfile"):
    dockerfile_path = os.path.join(directory, filename)
    with open(dockerfile_path, 'w+') as dockerfile:
        dockerfile.write(code)
    return dockerfile_path