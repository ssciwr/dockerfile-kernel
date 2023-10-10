Arg
===

Sets `Build Arguments <https://docs.docker.com/build/guide/build-args/>`_  for testing purposes when building Dockerfiles.

Usage
-----
To set Build Arguments:

.. code-block::

    %arg <name>=<value> (<name2>=<value2> <name3>=<value3> ...)

.. image:: /_gifs/magics/arg_set.gif
    :alt: Video of setting arg

To list current Build Arguments (default lists all):

.. code-block::

    %arg list
    %arg ls <name> (<name1> <name2> ...)

.. image:: /_gifs/magics/arg_list.gif
    :alt: Video of listing args

To remove current Build Arguments (default removes all)

.. code-block::

    %arg remove
    %arg rm <name> (<name1> <name2> ...)

.. image:: /_gifs/magics/arg_remove.gif
    :alt: Video of removing args

Caution
+++++++
The arg syntax is designed for testing purposes and cannot be exported, since it does not match the Dockerfile syntax.
Please use the Dockerfile `Build Arguments <https://docs.docker.com/build/guide/build-args/>`_ before exporting Dockerfiles.


Examples
--------

.. code-block::

    %arg VERSION=3.1.4

    %arg ls VERSION

    %arg rm VERSION
