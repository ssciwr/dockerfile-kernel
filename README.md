# dockerfile-kernel

This implements a Jupyter kernel to interpret Dockerfiles.

**This is currently work in progress between me and a group of students**

## Installation

Currently, the following prerequisites need to be met:

* Linux only (?)
* Docker needs to be installed
* The user needs to be in the `docker` group (see e.g. https://askubuntu.com/a/739861)
* JupyterLab >= 4.0.0 needs to be installed

You can then install the kernel with:

```bash
git clone https://github.com/dokempf/dockerfile-kernel.git
cd dockerfile-kernel
python -m pip install -e .
python -m pip install -e ./docker_export
python docker_kernel/install.py
pip install shell_extension/dist/shell_extension-0.1.0-py3-none-any.whl
pip install import_extension/dist/import_extension-0.1.0-py3-none-any.whl
```

Then, running `jupyter lab` you should be able to run the prototype.

## Testing
You can execute tests by installing pytest via `pip install -U pytest`.
Run `pytest` to execute the tests.
##### Included Tests
- Compare Dockerfile image ids after executing in notebook versus docker api
  - Implemented in `test_image_ids.py.`
  - How to add new test cases:
    1. Add a new *directory* in `test/test_envs`
    2. Include a Dockerfile (named `[something.]Dockerfile`)
    3. Add further files to the directory as context if required by the Dockerfile

## Links

* https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html
* https://github.com/pygments/pygments/blob/master/pygments/lexers/_mapping.py#L139
* https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.ImageCollection.build

