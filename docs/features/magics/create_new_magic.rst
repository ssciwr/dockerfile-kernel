How to Create a New Magic
=========================

This is a step by step example on how to create a new magic.

The magic created is the `random_int` magic. It returns one or more random integers between two integers
while handling some user errors before they occur.

1. Create a Base Class
++++++++++++++++++++++

First a class named the same as the magic must be created.
It needs to inherit the base ``Magic`` class.

.. code-block:: python

    class RandomInt(Magic):

        def __init__(self, kernel, *args, **flags):
            super().__init__(kernel, *args, **flags)

The ``Magic`` class provides four methods to be overwritten.

.. code-block:: python

    class RandomInt(Magic):

        def __init__(self, kernel, *args, **flags):
            super().__init__(kernel, *args, **flags)

        @staticmethod
        def REQUIRED_ARGS():
            return ([], 0)

        @staticmethod
        def ARGS_RULES():
            return {}

        @staticmethod
        def VALID_FLAGS():
            return {}

        def _execute_magic(self):
            pass

2. Defining Arguments
+++++++++++++++++++++

``REQUIRED_ARGS`` defines what arguments are expected and the index of the first *optional* argument.

In the case of `random_int` there are three arguments:

1. stop
2. start *(opt.)*
3. step *(opt.)*

``stop`` is required and defines the upper integer limit of the range to concider. The optional ``start``
defines the lower limit which will be implicit otherwise. The same holds for ``step``, which defines
the difference between possible integers.

To implement this change to ``REQUIRED_ARGS`` method to

.. code-block:: python

    @staticmethod
    def REQUIRED_ARGS() -> tuple[list[str], int]:
        # 'start' at index 1 is the first optional arg
        return (["stop", "start", "step"], 1)

3. Argument Rules
+++++++++++++++++

To do some error handling, conditions that arguments must meet can be defined by using *lambda* functions.

In this case we want all of our arguments to be positive integers only. If not, a custom error message
should be displayed as output of the cell.

Change ``ARGS_RULES`` to

.. code-block:: python

    @staticmethod
    def ARGS_RULES():
        is_positive_integer = lambda arg: arg.isdigit()
        return {
            0: [(is_positive_integer,
                 "Stop must be a positive integer")],
            1: [(is_positive_integer,
                 "Start must be a positive integer")],
            2: [(is_positive_integer,
                 "Step must be a positive integer")]
        }

4. Define Flags
+++++++++++++++

Other than arguments which can only be assigned by position, magics can also be used with flags.

Flags must have a *long name* and a *description*. Optionally they can have a *default* value and a *short name*.

In the `random_int` magic a `results` flag will be implemented. This will tell the magic how many results
should be returned. Its `short name` is `r` and the `default` is `1`.

Set `short name` / `default` to ``None`` if they should be left out.

*Note:* Even though the default is an integer, a string is provided. This is because user input is always a string and must be casted

.. code-block:: python

    @staticmethod
    def VALID_FLAGS():
        return {
            "results": {
                "short": "r",
                "default": "1",
                "desc": "Determines the number of results"
            }
        }

5. Magic Functionality
++++++++++++++++++++++

To have the magic do something the ``_execute_magic()`` method is used.

Before the magic executes, it is checked that

1. All required arguments are present
2. All arguments meet the requirements set by the `lambda` fucntions
3. All flags provided are valid

If no errors occur, one can now use the arguments and flags as well as default values for the non
required arguments...

.. code-block:: python

    def _execute_magic(self):
        stop = int(self._args[0])
        start = int(self._get_default_arg(1, "0"))
        step = int(self._get_default_arg(2, "1"))
        results = int(_get_default_flag("results", "r", "1"))

... some further conditions can be checked ...

.. code-block:: python

    def _execute_magic(self):
        ...
        if start >= stop:
            raise MagicError("Empty range: start must be smaller than stop")

... and a result can be output ...

.. code-block:: python

    def _execute_magic(self):
        ...
        for i in range(results):
            r = random.randrange(start, stop, step)
            self._kernel.send_response(str(r))

6. Final Result
+++++++++++++++

.. code-block:: python

    class RandomInt(Magic):

        def __init__(self, kernel, *args, **flags):
            super().__init__(kernel, *args, **flags)

        @staticmethod
        def REQUIRED_ARGS() -> tuple[list[str], int]:
            return (["stop", "start", "step"], 1)

        @staticmethod
        def ARGS_RULES():
            is_positive_integer = lambda arg: arg.isdigit()
            return {
                0: [(is_positive_integer,
                    "Stop must be a positive integer")],
                1: [(is_positive_integer,
                    "Start must be a positive integer")],
                2: [(is_positive_integer,
                    "Step must be a positive integer")]
            }

        @staticmethod
        def VALID_FLAGS():
            return {
                "results": {
                    "short": "r",
                    "default": "1",
                    "desc": "Determines the number of results"
                }
            }

        def _execute_magic(self):
            stop = int(self._args[0])
            start = int(self._get_default_arg(1, "0"))
            step = int(self._get_default_arg(2, "1"))
            results = int(_get_default_flag("results", "r", "1"))

            if start >= stop:
                raise MagicError("Empty range: start must be smaller than stop")

            for i in range(results):
                r = random.randrange(start, stop, step)
                self._kernel.send_response(str(r))