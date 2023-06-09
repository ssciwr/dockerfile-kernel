import docker
import io
import json
from .magics import detect_magic, call_magic

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
        magic, args, flags = detect_magic(code)

        if magic is not None:
            try:
                response = call_magic(self, magic, *args, **flags)
            except TypeError as e:
                response = e.args
            self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": "\n".join(response)})
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expression': {}}

        if self._sha1 is not None:
            code = f"FROM {self._sha1}\n{code}"
            
        f = io.BytesIO(code.encode('utf-8'))   
        for logline in self._api.build(fileobj=f, rm=True):
            loginfo = json.loads(logline.decode())

            if 'aux' in loginfo:
                self._sha1 = loginfo['aux']['ID']
        
            if 'stream' in loginfo:
                log = loginfo['stream']
                if log.strip() != "":
                    self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": log})

        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expression': {}}

    def tag_image(self, name: str, tag="latest", image_id: str|None=None):
        """ Tag an image.

        Parameters
        ----------
        name: str
            Image name to be assigned.
        tag: str, optional
            Typically a specific version or variant of an image.
        image_id: str | None, optional
            Id of image to be saved.
            If not specified, current image id is used.
        
        Return
        ------
        None
        """
        if self._sha1 is None and image_id is None:
            self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": "Error storing image: No image found"})
            return
        
        if name not in self._tags:
            self._tags[name] = {}

        image_id = self._sha1 if image_id is None else image_id
        self._tags[name][tag] = image_id

        image_str = image_id.removeprefix("sha256:")
        image_str = f"{image_str[:10]}..." if len(image_str) >= 10 else image_str
        self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": f"Image {image_str} tagged as \"{name}:{tag}\""})