Dockerfile Kernel Documentation
=================================

Contents
--------
.. toctree::
   :maxdepth: 2

   features/index
   docstring

Dockerfile Kernel
-----------------

This implements a JupyterLab kernel to interpret Dockerfiles.

**This is the result of a student's practical.**

Please consider :ref:`the important information <important_information>` before starting.

Setup
^^^^^

Prerequisites
+++++++++++++
* Tested on Linux only
* `Docker <https://docs.docker.com/engine/install/ubuntu/>`_ needs to be installed
* The user needs to be in the `docker` group (see e.g. `here <https://askubuntu.com/a/739861>`_)
* `JupyterLab <https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html>`_ >= 4.0.0 needs to be installed
.. _node_req:
* *(optional)* `Node.js <https://nodejs.org/en/download/package-manager>`_ >= 18 needs to be installed for :ref:`frontend extensions <installation_frontend>`

Installation
++++++++++++
.. code-block:: console

   $ git clone https://github.com/MarvinWeitz/dockerfile-kernel.git
   $ cd dockerfile-kernel
   $ python -m pip install -e .
   $ python -m dockerfile_kernel.install

.. _installation_frontend:
Installation frontend extensions *(optional)*
+++++++++++++++++++++++++++
:ref:`Node.js required <node_req>`

.. code-block:: console

   $ python -m pip install -e ./docker_extension
   $ python -m pip install -e ./docker_extension/export/


Execution
^^^^^^^^^
`jupyter lab`

.. _important_information:
!!! Important Information !!!
^^^^^^^^^^^^^^^^^^^^^

Space requirements
++++++++++++++++++
The kernel uses a temporary directory as a build context for the Dockerfile.

The inital build context is set to the directory JupyterLab was started in.
A :doc:`warning <./features/frontend/build_context>` is displayed in case this directory is
large **only** if frontend extensions are installed.

Please make sure that you have enough space available to copy the
:doc:`build context <./features/magics/context>` directory or use a
:ref:`dockerignore <dockerignore>` file to limit the build context.

Restraints
++++++++++
There are some features of Docker that are not (yet) working with the Dockerfile Kernel:

* `escape <https://docs.docker.com/engine/reference/builder/#escape>`_ can't be interpreted by the kernel
* `ONBUILD <https://docs.docker.com/engine/reference/builder/#onbuild>`_ is not producing the same hash id when executing a Dockerfile in the kernel versus the Docker daemon

Other
+++++

* The output of a cell can get lengthy. To activate scrollable output see `here <https://stackoverflow.com/a/50641638/11785440>`_.
* See :ref:`here <dockerignore_important>` before using dockerignore files.