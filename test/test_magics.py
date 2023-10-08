import sys
import pytest
import docker
import os
import json
from io import StringIO

from nbconvert.preprocessors import ExecutePreprocessor
from nbformat import read
from jupyter_client import KernelManager

from utils import convertDockerfileToNotebook


def generateKernelId(test_directory, dockerfile_name):
    notebook_string = convertDockerfileToNotebook(os.path.join(test_directory, dockerfile_name))

    with StringIO(notebook_string) as f:
        notebook = read(f, as_version=4)

    exec_preprocessor = ExecutePreprocessor(timeout=-1, kernel_name="docker")

    km = KernelManager(kernel_name="docker")
    notebook, _ = exec_preprocessor.preprocess(notebook, {'metadata': {'path': '.'}}, km=km)

    kernel_client = km.client()
    kernel_client.kernel_info()
    response = kernel_client.get_shell_msg()
    image_id = response.get("content", {}).get("imageId", None)

    return image_id

def generateDockerId(test_directory, dockerfile_name):
    docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')
    for logline in docker_api.build(path=test_directory, dockerfile=dockerfile_name, rm=True):
            loginfo = json.loads(logline.decode())
            if 'aux' in loginfo:
                docker_id = loginfo['aux']['ID']
    return docker_id

@pytest.mark.parametrize("Dockerfile_dir", os.listdir(os.path.join(os.path.dirname(__file__), "test_magics")))
def test_magics(Dockerfile_dir):
    test_directory = os.path.join(os.path.dirname(__file__), "test_magics", Dockerfile_dir)

    dockerfile_name = next(f for f in os.listdir(test_directory) if os.path.isfile(os.path.join(test_directory, f)) and f.lower().endswith("docker.dockerfile"))
    kernelfile_name = next(f for f in os.listdir(test_directory) if os.path.isfile(os.path.join(test_directory, f)) and f.lower().endswith("kernel.dockerfile")) # magic testfile has to end with "magic.dockerfile" e.g. mymagic_magic.dockerfile
    kernel_id = generateKernelId(test_directory, kernelfile_name)
    docker_id = generateDockerId(test_directory, dockerfile_name)
    assert kernel_id == docker_id, "Kernel Id and Docker Id should be the same"