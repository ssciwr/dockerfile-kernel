# dockerfile-kernel

This implements a JupyterLab kernel to interpret Dockerfiles.

## Features

- Line-based execution of Dockerfiles in JupyterLab
- Conveniently launch shell sessions running in a container created from the current image by clicking on a button.
- Command auto-completion
- Syntax Highlighting
- Help text integration with the `?` operation
- Export and Import from Dockerfiles
- Custom magics for e.g.
  - Tag the current Docker image with `%tag myimage:latest`
  - Easily follow best practices of installation with `%install apt <packagename>` (will expand to a `RUN` command doing all the required setup and cleanup). Also implemented for `pip` and `npm`.
  - Manipulate build arguments with `%arg`
  - Get an overview of existing build stages with `%stages`
  - Manipulate the build context with `%context`

## Prerequisites

- Currently, only Linux is supported
- [Docker](https://docs.docker.com/engine/install/ubuntu/) needs to be installed
- The user needs to be in the `docker` group (see e.g. [here](https://askubuntu.com/a/739861))
- [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html) >= 4.0.0 needs to be installed

## Installation

With pip:

```bash
python -m pip install dockerfile-kernel
```

With conda:

```bash
conda install -c conda-forge dockerfile-kernel
```

#### Execution

`jupyter lab`
