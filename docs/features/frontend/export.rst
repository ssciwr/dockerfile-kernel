Export as Dockerfile
====================

Export the notebook as a valid Dockerfile.

Usage
-----

*File > Save and Export Notebook As... > Dockerfile*

.. image:: /_gifs/frontend/export.gif
    :alt: Video of exporting

The export focuses on restorability. The goal is to have the same notebook when :doc:`importing <import>` the exported notebook back into JupyterLab.

This means all markdown cells as well as the cells containing magic commands will also be present in the exported Dockerfile. They
will be commented out.

Example
-------
The notebook

+---+---------------------------------------+-----------+
| # | Content                               | Cell Type |
+===+=======================================+===========+
| 1 + FROM ubuntu                           | Code      |
+---+---------------------------------------+-----------+
| 2 + %magics                               | Code      |
+---+---------------------------------------+-----------+
| 3 + ### Some Heading                      | Markdown  |
+---+---------------------------------------+-----------+
| 4 + RUN echo "Export this file please"    | Code      |
+---+---------------------------------------+-----------+

Will result in this Dockerfile

.. code-block:: docker

    FROM ubuntu

    #mg %magics

    #md ### Some Heading

    RUN echo "Export this file please"
