import docker
import io
import json
from docker_kernel.magic import Magic

from ipykernel.kernelbase import Kernel

# The single source of version truth
__version__ = "0.0.1"

class DockerKernel(Kernel):
    implementation = "Dockerfile Kernel"
    implementation_version = __version__
    language = 'docker'
    language_version = docker.__version__
    language_info = {
        "name": 'docker',
        'mimetype': 'text/x-dockerfile-config',
        'file_extension': ".dockerfile"
    }
    banner = "Dockerfile Kernel"

    def __init__(self, *args, **kwargs):
        """Initialize the kernel."""
        super().__init__(**kwargs)
        self._api = docker.APIClient(base_url='unix://var/run/docker.sock')
        self._sha1: str | None = None
        self._tags: dict[str, dict[str, str]] = {}
        self._payload = []

    
    @property
    def default_tag(self):
        return "latest"
      
    def do_execute(self, code: str, silent: bool, store_history=True, user_expressions={}, allow_stdin=False):
        """ Execute user code.
        
        Parameters
        ----------
        code: str
            The code to be executed.
        silent: bool
            Whether to display output.
        store_history: bool
            Whether to record this code in history and increase the execution count. If silent is True, this is implicitly False.
        user_expressions: dict
            Mapping of names to expressions to evaluate after the code has run. You can ignore this if you need to.
        allow_stdin: bool
            Whether the frontend can provide input on request (e.g. for Python's `raw_input()`).

        Returns
        -------
        dict
            Specified [here](https://jupyter-client.readthedocs.io/en/stable/messaging.html#execution-results)
        """
        MagicClass, args, flags = Magic.detect_magic(code)
        self._payload = []

        ####################
        # Magic execution
        if MagicClass is not None:
            try:
                response = MagicClass(self, *args, **flags).call_magic()
            except TypeError as e:
                response = e.args
            self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": "\n".join(response)})
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        
        ####################
        # Docker execution
        code = self.create_build_stage(code)
        logs = self.build_image(code)
        for log in logs:
            self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": log})

        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        
    def do_complete(self, code: str, cursor_pos: int):
        """For now only provide completion for magics"""
        matches = []
        if code.startswith("%"):
            snippets = code.split(" ")
            if cursor_pos <= len(snippets[0]):
                code_magic = code.removeprefix("%")
                matches = [m for m in Magic.magics_names if m.startswith(code_magic)]
        
        return {
            "matches": matches,
            "cursor_end": cursor_pos,
            "cursor_start": cursor_pos,
            "metadata": {},
            "status": "ok",
        }

    def create_build_stage(self, code):
        """ Add current *_sha1* to the code."""
        if self._sha1 is not None:
            code = f"FROM {self._sha1}\n{code}"
        return code

    def build_image(self, code):
        """ Build docker image by passing input to the docker API."""
        f = io.BytesIO(code.encode('utf-8'))
        logs = [] 
        for logline in self._api.build(fileobj=f, rm=True):
            loginfo = json.loads(logline.decode())

            if 'aux' in loginfo:
                self._sha1 = loginfo['aux']['ID']
        
            if 'stream' in loginfo:
                log = loginfo['stream']
                if log.strip() != "":
                    logs.append(log)
        return logs
    
    def set_payload(self, source: str, text: str, replace: bool):
        """ Trigger frontend action via payloads. 
        
        Parameters
        ----------
        source: str
            action type, e.g. *'set_next_input'* to create a new cell
        text: str
            text contents of the cell to create
        replace: bool
            If true, replace the current cell in document UIs instead of inserting a cell. Ignored in console UIs.
        
        Returns
        -------
        NONE
        """
        self._payload =[{
            "source": source,
            "text": text,
            "replace": replace,
        }]
                    
    def tag_image(self, image_id: str, name: str, tag: str|None=None):
        """ Tag an image.
        Parameters
        ----------
        image_id: str
            Id of image to be saved.
        name: str
            Image name to be assigned.
        tag: str, optional
            Typically a specific version or variant of an image.
        
        Return
        ------
        None
        """
        tag = self.default_tag if tag is None else tag

        if name not in self._tags:
            self._tags[name] = {}

        self._tags[name][tag] = image_id
