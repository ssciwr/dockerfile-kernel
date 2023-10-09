Tag
===

Tag the *current image*. The tag is stored in the local docker daemon, so it
can be used outside the notbook as well.

If no tag is provided docker's default *latest* is used.

Usage
-----

.. code-block::

    %tag IMAGE[:TAG]

.. image:: /_gifs/magics/tag.gif
    :alt: Video of tag

Example
-------
To tag the current image as "fedora/httpd" with the tag "version1.0":

.. code-block::

    %tag fedora/httpd:version1.0

Further Information
-------------------
For further information visit the `official documentation <https://docs.docker.com/engine/reference/commandline/tag/>`_.


