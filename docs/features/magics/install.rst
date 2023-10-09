Install
=======

    Installs additional package(s) to the docker image utilizing different package managers, including the clean up process afterwards. Currenty, there are four package managers:
    apt(-get), pip, conda, conda with channel conda-forge and npm.

    Caveat: The specified package manager has to be available at the current build stage.

    After successfull execution, the magic sippet will be replaced by the actual code executed by the kernel to enable exporting of the resulting Dockerfile.



Usage
-----

>>> %install <package manager> <package1 (package2 package3 ...)>

Examples:

>>> %install apt foo

>>> %install pip foo bar