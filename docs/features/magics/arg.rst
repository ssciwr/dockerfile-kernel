Arg
===

Sets `Build Arguments <https://docs.docker.com/build/guide/build-args/>`_  for testing purposes when building Dockerfiles.

Usage
-----
To set Build Arguments:

.. code-block::

    %arg <key>=<value> (<key2>=<value2> <key3>=<value3> ...)


To list current Build Arguments (default lists all):

.. code-block::

    %arg list
    %arg ls <key> (<key1> <key2> ...)


To remove current Build Arguments (default removes all)

.. code-block::

    %arg remove
    %arg rm <key> (<key1> <key2> ...)



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
