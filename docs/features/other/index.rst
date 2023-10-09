Other Functionalities
======================

.. _dockerignore:

.dockerignore
-------------

The :doc:`build context <../magics/context>` used by the Dockerfile Kernel can be filtered
via a `.dockerignore` file.

See `here <https://docs.docker.com/engine/reference/builder/#dockerignore-file>`_ how they
work. Also see `here <https://docs.docker.com/develop/develop-images/guidelines/#exclude-with-dockerignore>`_
for a best practise regarding them.

.. _dockerignore_important:

**Important:** Dockerfile Kernel doesnt use the docker dameon to interpret the build context and
dockerignore files. This means the result of files are apllying the dockerignore file may vary.

We tried to *"miss"* files rather than include those that aren't by the docker daemon.
Still, errors could occur because of this.


Syntax Highlighting
-------------------

The notebook code support Dockerfile highlighting.


Auto Complete
-------------

Dockerfile Kernel provides auto completion by pressing the *tab* button in code.

.. image:: /_gifs/other/autocomplete.gif
    :alt: Video of autocomplete