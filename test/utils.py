import os
import uuid
import json
import docker
from io import StringIO

from nbconvert.preprocessors import ExecutePreprocessor
from nbformat import read
from jupyter_client import KernelManager


def convertDockerfileToNotebook(path_to_dockerfile):
    with open(path_to_dockerfile, "r", newline="\n") as dockerfile:
        lines = dockerfile.readlines()
        lines = "".join(lines).split("\n\n")
        content = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Dockerfile",
                    "language": "text",
                    "name": "docker",
                },
                "language_info": {
                    "file_extension": ".dockerfile",
                    "mimetype": "text/x-dockerfile-config",
                    "name": "docker",
                },
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }

    for line in lines:
        cell_type = "code"
        if line.startswith("# "):
            line = line[2:]
            if not line.startswith("%"):
                cell_type = "markdown"
        content["cells"].append(
            {
                "cell_type": cell_type,
                "execution_count": None,
                "id": str(uuid.uuid4()),
                "metadata": {},
                "outputs": [],
                "source": line,
            }
        )

    return json.dumps(content)


def generateKernelId(test_directory, dockerfile_name):
    notebook_string = convertDockerfileToNotebook(
        os.path.join(test_directory, dockerfile_name)
    )

    with StringIO(notebook_string) as f:
        notebook = read(f, as_version=4)

    exec_preprocessor = ExecutePreprocessor(timeout=-1, kernel_name="docker")

    km = KernelManager(kernel_name="docker")
    notebook, _ = exec_preprocessor.preprocess(
        notebook, {"metadata": {"path": "."}}, km=km
    )

    kernel_client = km.client()
    kernel_client.kernel_info()
    response = kernel_client.get_shell_msg()
    image_id = response.get("content", {}).get("imageId", None)

    return image_id


def generateDockerId(test_directory, dockerfile_name):
    docker_api = docker.APIClient(base_url="unix://var/run/docker.sock")
    for logline in docker_api.build(
        path=test_directory, dockerfile=dockerfile_name, rm=True
    ):
        loginfo = json.loads(logline.decode())
        if "aux" in loginfo:
            docker_id = loginfo["aux"]["ID"]
    return docker_id
