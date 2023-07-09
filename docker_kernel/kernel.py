import docker
import io
import json
import tarfile
import os
import tempfile, shutil
# from tempfile import TemporaryDirectory
from ipykernel.kernelbase import Kernel

from .magics.magic import Magic
from .utils.notebook import get_cursor_frame
from.magics.helper.errors import MagicError
from docker.errors import APIError

# The single source of version truth
__version__ = "0.0.1"

class DockerKernel(Kernel):
    implementation = "Dockerfile1 Kernel"
    implementation_version = __version__
    language = 'docker'
    language_version = docker.__version__
    language_info = {
        "name": 'docker',
        'mimetype': 'text/x-dockerfile-config',
        'file_extension': ".dockerfile"
    }
    banner = "Dockerfile1 Kernel"

    def __init__(self, *args, **kwargs):
        """Initialize the kernel."""
        super().__init__(**kwargs)
        self._api = docker.APIClient(base_url='unix://var/run/docker.sock')
        self._sha1: str | None = None
        self._payload = []
        self._intermedia_images = {}
        self._current_alias: str | None = None

    
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
        self._payload = []
        
        ####################
        # Magic execution
        try:
            MagicClass, args, flags = Magic.detect_magic(code)

            
            if MagicClass is not None:
                MagicClass(self, *args, **flags).call_magic()
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        except MagicError as e:
            self.send_response(str(e))
        
        ####################
        # Docker execution
        try:
            code = self.create_build_stage(code)
            self.build_image(code)
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        except Exception as e:
            self.send_response(str(e))


    def do_complete(self, code: str, cursor_pos: int):
        """Provide code completion
        
        Parameters
        ----------
        code: str
            The code already present
        cursor_pos: int
            The position in the code where completion is requested

        Returns
        -------
        complete_reply: dict

        See [here](https://jupyter-client.readthedocs.io/en/stable/messaging.html#completion) for reference
        """
        matches = []
        matches.extend(Magic.do_complete(code, cursor_pos))
        matches.sort()

        cursor_start, cursor_end = get_cursor_frame(code, cursor_pos)
        
        return {
            "status": "ok",
            "matches": matches,
            "cursor_start": cursor_start,
            "cursor_end": cursor_end,
            "metadata": {},
        }

    def create_build_stage(self, code):
        """
        Add current *_sha1* to the code.
        Replace base image alias or index with image id.
        COPY --from=[image alias/index] [src] [dest]
        -->
        COPY --from=[image id] [src] [dest]
        """
        self.start_a_new_layer(code)
        code = self.replace_base_image_with_id(code)
        if self._sha1 is not None:
            code = f"FROM {self._sha1}\n{code}"
        return code

    def replace_base_image_with_id(self, code):
        if '--from=' in code:
            code_seg = code.split(" ")
            contain_image = [s for s in code_seg if "--from" in s]
            image_alias = ''.join(contain_image).split("=")[1]
            base_image_id = list(self._intermedia_images.values())[int(image_alias)] if image_alias.isdigit() \
                else self._intermedia_images[image_alias]
            code = f"{code_seg[0]} --from={base_image_id} {' '.join(code_seg[2:])}"
        return code

    def start_a_new_layer(self, code):
        if code.startswith("FROM"):
            try:
                alias = code.split('as')[1].strip()
            except:
                alias = len(self._intermedia_images)
            self._current_alias = alias
            self._intermedia_images[alias] = ''

    def build_image(self, code):
        """ Build docker image by passing input to the docker API."""

        f = io.BytesIO(code.encode('utf-8'))
        logs = []
        current_working_directory = os.getcwd()
        dockerfile_path = os.path.join(current_working_directory, 'Dockerfile')
        with open(dockerfile_path, 'w') as df:
            df.write(code)
        for logline in self._api.build(path=current_working_directory, dockerfile=dockerfile_path, rm=True):
            loginfo = json.loads(logline.decode())

            if 'aux' in loginfo:
                self._sha1 = loginfo['aux']['ID']
                image_id = self._sha1.split(':')[1][:12]
                self._intermedia_images[self._current_alias]=image_id

            if 'stream' in loginfo:
                log = loginfo['stream']
                if log.strip() != "":
                    self.send_response(log)

    def send_response(self, content_text, stream=None, msg_or_type="stream", content_name="stdout"):
        stream = self.iopub_socket if stream is None else stream
        return super().send_response(stream, msg_or_type, {"name": content_name, "text": content_text})
    
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

        See [here](https://jupyter-client.readthedocs.io/en/stable/messaging.html#payloads-deprecated) for reference

        """
        self._payload =[{
            "source": source,
            "text": text,
            "replace": replace,
        }]

    def tag_image(self, name: str, tag: str|None=None):
        """ Tag an image.
        Parameters
        ----------
        name: str
            Image name to be assigned.
        tag: str, optional
            Typically a specific version or variant of an image.

        Return
        ------
        None
        """

        if not self._sha1==None:
            image = self._sha1.split(":")[1][:12]
            try:
                self._api.tag(self._sha1, name, tag)
                self.send_response(f"Image {image} is tagged with: {name}:{tag if tag is not None else 'latest'}")
            except Exception as e:
                raise MagicError(str(e))
        else:
            raise MagicError("no valid image, please build the image first")


