import pytest
import os

from utils import generateKernelId, generateDockerId


@pytest.mark.parametrize(
    "Dockerfile_dir", os.listdir(os.path.join(os.path.dirname(__file__), "test_envs"))
)
def test_image_ids(Dockerfile_dir):
    test_path = os.path.join(os.path.dirname(__file__), "test_envs", Dockerfile_dir)

    dockerfile_name = next(
        f
        for f in os.listdir(test_path)
        if os.path.isfile(os.path.join(test_path, f))
        and f.lower().endswith("dockerfile")
    )

    kernel_id = generateKernelId(test_path, dockerfile_name)
    docker_id = generateDockerId(test_path, dockerfile_name)
    assert kernel_id == docker_id, "Kernel Id and Docker Id should be the same"
