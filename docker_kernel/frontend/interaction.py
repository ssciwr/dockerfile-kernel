from ipylab import JupyterFrontEnd

class FrontendInteraction():
    def __init__(self, app: JupyterFrontEnd):
        self.app = app
    
    def handle_code(self, code: str):
        if code.rstrip().endswith("?"):
            hook = code.split(" ")[-1].removesuffix("?")
            self._execute_helper(hook)
            return True
        else:
            return False

    def _execute_helper(self, hook):
        self.app.commands.execute("helper:open", {"hook": hook})
