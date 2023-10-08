import sys
import pytest
import os

from utils import generateKernelId, generateDockerId

@pytest.mark.parametrize("Dockerfile_dir", (d for d in os.listdir(os.path.join(os.path.dirname(__file__), "test_envs"))))
def test_image_ids(Dockerfile_dir):
    test_path = os.path.join(os.path.dirname(__file__), "test_envs", Dockerfile_dir)
    test_directories = [os.path.join(test_path, d) for d in next(os.walk(test_path))[1]]
    
    for test_directory in test_directories:
        dockerfile_name = next(f for f in os.listdir(test_directory) if os.path.isfile(os.path.join(test_directory, f)) and f.lower().endswith("dockerfile"))
        kernel_id = generateKernelId(test_directory, dockerfile_name)
        docker_id = generateDockerId(test_directory, dockerfile_name)
        assert kernel_id == docker_id, "Kernel Id and Docker Id should be the same"
