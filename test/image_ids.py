import unittest
import sys

import docker
import os
import json
from io import StringIO

from nbconvert.preprocessors import ExecutePreprocessor
from nbformat import read
from jupyter_client import KernelManager

from utils import convertDockerfileToNotebook


def generateKernelId(dockerfile_path):
    notebook_string = convertDockerfileToNotebook(dockerfile_path)

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

def generateDockerId(dockerfile_path):
    docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')
    with open(dockerfile_path, "rb") as dockerfile:
        for logline in docker_api.build(fileobj=dockerfile):
            loginfo = json.loads(logline.decode())

            if 'aux' in loginfo:
                docker_id = loginfo['aux']['ID']
    return docker_id


class TestImageIds(unittest.TestCase):
    def test_image_ids(self):
        test_file_paths = []
        try:
            print(os.path.dirname(__file__))
            test_path = sys.argv[1]
        except IndexError:
            test_path = os.path.join(os.path.dirname(__file__), "dockerfiles")
        finally:
            for file in os.listdir(test_path):
                if file.lower().endswith("dockerfile"):
                    test_file_paths.append(os.path.join(test_path, file))
        for file_path in test_file_paths:
            kernel_id = generateKernelId(file_path)
            docker_id = generateDockerId(file_path)
            self.assertEqual(kernel_id, docker_id, "Kernel Id and Docker Id should be the same")

if __name__ == "__main__":
    unittest.main(argv=['filepath'])