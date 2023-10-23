import pytest
import os

from utils import generateKernelId, generateDockerId


@pytest.mark.parametrize(
    "Dockerfile_dir", os.listdir(os.path.join(os.path.dirname(__file__), "test_magics"))
)
def test_magics(Dockerfile_dir):
    test_directory = os.path.join(
        os.path.dirname(__file__), "test_magics", Dockerfile_dir
    )

    dockerfile_name = next(
        f
        for f in os.listdir(test_directory)
        if os.path.isfile(os.path.join(test_directory, f))
        and f.lower().endswith("docker.dockerfile")
    )
    kernelfile_name = next(
        f
        for f in os.listdir(test_directory)
        if os.path.isfile(os.path.join(test_directory, f))
        and f.lower().endswith("kernel.dockerfile")
    )  # magic testfile has to end with "magic.dockerfile" e.g. mymagic_magic.dockerfile
    kernel_id = generateKernelId(test_directory, kernelfile_name)
    docker_id = generateDockerId(test_directory, dockerfile_name)
    assert kernel_id == docker_id, "Kernel Id and Docker Id should be the same"
