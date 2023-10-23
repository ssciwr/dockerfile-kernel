import json
import os
import sys

from jupyter_client.kernelspec import KernelSpecManager
from IPython.utils.tempdir import TemporaryDirectory

kernel_json = {
    "argv": [sys.executable, "-m", "dockerfile_kernel", "-f", "{connection_file}"],
    "display_name": "Dockerfile",
    "language": "text",
}


if __name__ == "__main__":
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755)  # Starts off as 700, not user readable
        with open(os.path.join(td, "kernel.json"), "w") as f:
            json.dump(kernel_json, f, sort_keys=True)

        print("Installing Jupyter kernel spec for DockerKernel")
        KernelSpecManager().install_kernel_spec(td, "docker", prefix=sys.prefix)
