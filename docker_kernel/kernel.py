import shutil
import tempfile

import docker
import json
import os
from ipykernel.kernelbase import Kernel

from ipylab import JupyterFrontEnd

from .magics.magic import Magic
from .utils.notebook import get_cursor_frame
from .magics.helper.errors import MagicError
from .frontend.interaction import FrontendInteraction
from docker.errors import APIError

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
        self._payload = []
        self._build_stage_indices: dict[int, tuple[int, str | None]] = {}
        self._latest_index: int | None = None
        self._build_stage_aliases = {}
        self._current_alias: str | int | None = None
        self._frontend = None
      
    @property
    def kernel_info(self):
        info = super().kernel_info
        info["imageId"] = self._sha1
        return info
      
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
        
        ####################
        # Prepare kernel for code execution
        self._payload = []
        self._frontend = self._frontend if self._frontend is not None else FrontendInteraction(JupyterFrontEnd())
        
        ####################
        # Magic execution
        try:
            MagicClass, args, flags = Magic.detect_magic(code)

            if MagicClass is not None:
                MagicClass(self, *args, **flags).call_magic()
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        except MagicError as e:
            self.send_response(str(e))
            return {'status': 'error', "ename": "MagicError", "evalue": str(e), "traceback": []}

        ####################
        # Frontend execution
        frontend_interacted = self._frontend.handle_code(code)
        if frontend_interacted:
            return {'status': 'error', "ename": "FrontEndExecuted", "evalue": "", "traceback": []}
        
        ####################
        # Docker execution
        try:
            build_code = self.create_build_stage(code)
            self.build_image(build_code)
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        except APIError as e:
            if e.explanation is not None:
                self.send_response(str(e.explanation))
            else:
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
        code = self._replace_alias(code)
        if self._sha1 is not None:
            code = f"FROM {self._sha1}\n{code}"
        return code

    def _replace_alias(self, code):
        code_segments = code.lower().strip().split(" ")
        try:
            # Get code segment where image is specified
            image_segment = next(x for x in code_segments if x.startswith('--from='))
        except StopIteration:
            return code
        
        try:
            image_alias = image_segment.split("=")[1]
            if image_alias.isdigit():
                base_image_id = self._build_stage_indices[int(image_alias)]
            else:
                base_image_id = self._build_stage_indices[self._build_stage_aliases[image_alias]]
        except IndexError:
            base_image_id = ""
        except KeyError:
            base_image_id = image_alias
            self.send_response(f"Note: Build stage {image_alias} is not known.")
            self.send_response(f"Attempting to use image with name {image_alias}...")
        return f"{code_segments[0]} --from={base_image_id} {' '.join(code_segments[2:])}"

    def _create_build_stage(self, code, image_id):
        if not code.lower().strip().startswith('from'):
            return
        
        _, *remain = code.split(' ')
        
        self._latest_index = self._latest_index + 1 if self._latest_index is not None else 0

        alias = None
        if len(remain) > 1 and remain[1] == 'as':
            alias = remain[2]
            self._build_stage_aliases[alias] = self._latest_index
        self._build_stage_indices[self._latest_index] = (image_id, alias)

    def build_image(self, code):
        """ Build docker image by passing input to the docker API."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                shutil.copytree(os.getcwd(), tmp_dir, dirs_exist_ok=True)
                dockerfile_path = self._create_dockerfile(code, tmp_dir)
            except shutil.Error as e:
                self.send_response(str(e))

            for logline in self._api.build(path=tmp_dir,dockerfile=dockerfile_path, rm=True):
                loginfo = json.loads(logline.decode())
                if 'error' in loginfo:
                    self.send_response(f'error:{loginfo["error"]}\n')
                if 'aux' in loginfo:
                    self._sha1 = loginfo['aux']['ID']
                    self._create_build_stage(code, loginfo['aux']['ID'])
                if 'stream' in loginfo:
                    log = loginfo['stream']
                    if log.strip() != "":
                        self.send_response(log)

    def _create_dockerfile(self, code, tmp_dir):
        dockerfile_path = os.path.join(tmp_dir, 'Dockerfile')
        with open(dockerfile_path, 'w+') as dockerfile:
            dockerfile.write(code)
        return dockerfile_path


    def send_response(self, content_text, stream=None, msg_or_type="stream", content_name="stdout"):
        stream = self.iopub_socket if stream is None else stream
        super().send_response(stream, msg_or_type, {"name": content_name, "text": content_text})
    
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


