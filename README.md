# dockerfile-kernel

This implements a JupyterLab kernel to interpret Dockerfiles.

**This is the result of a student's practical.**

## Setup

#### Prerequisites

- Tested on Linux only
- [Docker](https://docs.docker.com/engine/install/ubuntu/) needs to be installed
- The user needs to be in the `docker` group (see e.g. [here](https://askubuntu.com/a/739861))
- [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html) >= 4.0.0 needs to be installed
- _(optional)_ [Node.js](https://nodejs.org/en/download/package-manager) >= 18 needs to be installed for frontend extensions to be installed

#### Installation

```bash
git clone https://github.com/MarvinWeitz/dockerfile-kernel.git
cd dockerfile-kernel
python -m pip install -e .
python -m dockerfile_kernel.install
```

_(optional)_ To install the frontend extensions

```bash
python -m pip install -e ./docker_extension
python -m pip install -e ./docker_extension/export/
```

#### Execution

`jupyter lab`
