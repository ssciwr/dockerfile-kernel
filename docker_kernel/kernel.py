import shutil
import tempfile

import docker
import json
import os
from ipykernel.kernelbase import Kernel

from ipylab import JupyterFrontEnd

from .magics.magic import Magic
from .utils.notebook import get_cursor_frame, get_cursor_words, get_line_start
from .utils.filesystem import create_dockerfile, remove_tmp_dir,copy_files
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
        'mimetype': 'text/x-dockerfile',
        'codemirror_mode': "Dockerfile",
        'file_extension': ".dockerfile"
    }
    banner = "Dockerfile Kernel"

    # source of keywords: https://docs.docker.com/engine/reference/builder/
    keywords = {"ARG": [], "ADD": ["--chown=", "--chmod=", "--checksum=", "--keep-git-dir=true", "--link"], "CMD": [], "ENV": [], "COPY": ["--chown=", "--chmod=", "--from=", "--link"], "ENTRYPOINT": [], "FROM": ["AS ", "--platform="], "EXPOSE": [], "HEALTHCHECK": ["--intervall=", "--timeout=", "--start-period=", "--start-interval=", "--retries="],
                "LABEL": [], "ONBUILD": [], "RUN": ["--mount=", "--network", "--privileged", "--security", "--mount=type=bind", "--mount=type=cache", "--mount=type=tmpfs", "--mount=type=secret", "--mount=type=ssh", "--network=default", "--network=none", "--network=host", "--security=insecure", "--security=sandbox"], "SHELL": [], "STOPSIGNAL": [], "USER": [], "VOLUME": [], "WORKDIR": []}

    def __init__(self, *args, **kwargs):
        """Initialize the kernel."""
        super().__init__(**kwargs)
        self._api = docker.APIClient(base_url='unix://var/run/docker.sock')
        self._sha1: str | None = None
        self._buildargs = {}
        self._payload = []
        self._build_stage_indices: dict[int, tuple[str, str | None]] = {}
        self._latest_index: int | None = None
        self._build_stage_aliases = {}
        self._build_context_dir: str = os.getcwd() # directory the kernel was started in
        self._frontend = None
        self._tmp_dir = tempfile.TemporaryDirectory()
        copy_files(self._build_context_dir, self._tmp_dir.name)

    def __del__(self):
        remove_tmp_dir(self._tmp_dir)

    @property
    def kernel_info(self):
        info = super().kernel_info
        info["imageId"] = self._sha1
        return info
    
    ########################################
    # Core functionalities
    ########################################

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
            self.build_image(code)
            # self.send_response(f"temp dir:{self._tmp_dir.name}\n")
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        except APIError as e:
            if e.explanation is not None:
                self.send_response(str(e.explanation))
            else:
                self.send_response(str(e))

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

    ########################################
    # Notebook interaction
    ########################################

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
        self._payload = [{
            "source": source,
            "text": text,
            "replace": replace,
        }]

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
        line_start = get_line_start(code, cursor_pos)
        cursor_start, cursor_end = get_cursor_frame(code, cursor_pos)
        word, _ = get_cursor_words(code, cursor_pos)
        partial_word = word[:cursor_pos - cursor_start]

        # Magic command completion
        if line_start and line_start.startswith("%"):
            matches.extend(Magic.do_complete(code, cursor_pos))

        # Docker command completion
        if line_start not in self.keywords:
            matches.extend(k for k in self.keywords if k.startswith(
                partial_word.upper()))
        else:
            matches.extend(flag for flag in self.keywords[line_start] if flag.startswith(
                partial_word.lower()
            ))

        matches.sort()
        return {
            "status": "ok",
            "matches": matches,
            "cursor_start": cursor_start,
            "cursor_end": cursor_end,
            "metadata": {},
        }
    
    ########################################
    # Docker functionality
    ########################################

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

        if not self._sha1 == None:
            image = self._sha1.split(":")[1][:12]
            try:
                self._api.tag(self._sha1, name, tag)
                self.send_response(
                    f"Image {image} is tagged with: {name}:{tag if tag is not None else 'latest'}")
            except Exception as e:
                raise MagicError(str(e))
        else:
            raise MagicError("no valid image, please build the image first")

    def build_image(self, code):
        """ Build docker image by passing input to the docker API."""
        tmp_dir = self._tmp_dir.name
        build_code = self.create_build_stage(code)
        dockerfile_path = create_dockerfile(build_code, tmp_dir)

        for logline in self._api.build(buildargs=self._buildargs, path=tmp_dir, dockerfile=dockerfile_path, rm=True):
            loginfo = json.loads(logline.decode())
            if 'error' in loginfo:
                self.send_response(f'\nerror: {loginfo["error"]}\n')
                return
            if 'aux' in loginfo:
                self._sha1 = loginfo['aux']['ID']
            if 'stream' in loginfo:
                log = loginfo['stream']
                if log.strip() != "":
                    self.send_response(log)

        self._save_build_stage(code, self._sha1)

    def _save_build_stage(self, code, image_id):
        if not code.lower().strip().startswith(("from", "arg", "#")):
            _, alias = self._build_stage_indices[self._latest_index]
            self._build_stage_indices[self._latest_index] = (image_id, alias)
            return
        
        _, *remain = code.split(' ')
        
        self._latest_index = self._latest_index + 1 if self._latest_index is not None else 0

        alias = None
        if len(remain) > 1 and remain[1] == 'as':
            alias = remain[2]
            self._build_stage_aliases[alias] = self._latest_index
        self._build_stage_indices[self._latest_index] = (image_id, alias)

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
                base_image_id = self._build_stage_indices[int(image_alias)][0]
            else:
                base_image_id = self._build_stage_indices[self._build_stage_aliases[image_alias]][0]
        except IndexError:
            base_image_id = ""
        except KeyError:
            base_image_id = image_alias
            self.send_response(f"Note: Build stage {image_alias} is not known.")
            self.send_response(f"Attempting to use image with name {image_alias}...")
        return f"{code_segments[0]} --from={base_image_id} {' '.join(code_segments[2:])}"
    
    @property
    def buildargs(self) -> dict[str, str]:
        """Getter for current build arguments"""
        return self._buildargs
    
    @buildargs.setter
    def buildargs(self, buildargs: dict[str, str]):
        """Getter for current build arguments"""  
        self._buildargs.update(buildargs)
    
    def remove_buildargs(self, all: bool=False, *names: str):
        """Remove current build arguments specified by name

        Parameters
        ----------
        bool=False: str
            If True remove all current build arguments, by default False
        *names: str
            Names of the bbuild arguments to be removed

        Returns
        -------
        None
        """
        if all:
            self._buildargs = {}
        else:
            self.send_response(names)
            for name in names:
                self.buildargs.pop(name)
