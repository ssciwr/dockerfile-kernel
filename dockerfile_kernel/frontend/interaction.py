from ipylab import JupyterFrontEnd


class FrontendInteraction:
    """Handles frontend interactions triggered by the :py:class:`kernel.DockerKernel`."""

    def __init__(self, app: JupyterFrontEnd):
        self.app = app

    def handle_code(self, code: str):
        """Entry method to be used in every code execution.

        All subsequent functionality will be called from this method.

        Args:
            code (str): The user's code.

        Returns:
            bool: Indicates if further code should be executed by the :py:class:`kernel.DockerKernel`.
        """
        if code.rstrip().endswith("?"):
            hook = code.split(" ")[-1].removesuffix("?")
            self._execute_helper(hook)
            return True
        else:
            return False

    def _execute_helper(self, hook: str):
        """Executes the helper frontend.

        Args:
            hook (str): Hook for the website.
        """
        self.app.commands.execute("helper:open", {"hook": hook})

    def build_context_warning(self):
        return self.app.commands.execute("docker:context_warning")
