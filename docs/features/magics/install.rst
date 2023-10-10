Install
=======

Installs additional packages to the docker image utilizing different package managers, including
the clean up process afterwards.

Usage
-----

.. code-block::

    %install <package manager> <package1 (package2 package3 ...)>

.. image:: /_gifs/magics/install.gif
    :alt: Video of install

After successfull execution, the magic snippet will be replaced by the actual code executed by
the kernel to enable :doc:`exporting <../frontend/export>` of the resulting Dockerfile.

Available Package Managers
^^^^^^^^^^^^^^^^^^^^^^^^^^

* apt
* pip
* conda
* conda-forge
* npm

conda-forge
+++++++++++
conda-forge is conda with the *conda-forge* channel

Caution
+++++++
The specified package manager has to be available at the current build stage.

Examples
--------

.. code-block::

    %install apt foo

    %install pip foo bar
