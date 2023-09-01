import shutil
import tempfile

import docker
import json
import os
from typing import Tuple
from ipykernel.kernelbase import Kernel

from ipylab import JupyterFrontEnd

from .magics.magic import Magic
from .utils.notebook import get_cursor_frame, get_cursor_words, get_line_start
from .utils.filesystem import create_dockerfile, copy_files, empty_dir, get_dir_size
from .utils.dockerignore import preporcessed_dockerignore, dockerignore
from .magics.helper.errors import MagicError
from .frontend.interaction import FrontendInteraction
from docker.errors import APIError
from prettytable import PrettyTable

# The single source of version truth
__version__ = "0.0.1"


class DockerKernel(Kernel):
    """Docker kernel for Jupyter.
    
    Based on [IPython's kernel machinery](https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html).
    Interprets Dockerfile commands in Jupyter Lab's notebooks.
    """
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
        self._frontend = None
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._build_context_dir: str | None = None
        self._build_context_warning_shown = False
        # 100MB in bytes
        if get_dir_size(os.getcwd()) < 100_000_000:
            self._build_context_dir: str | None = os.getcwd()
        self.change_build_context_directory(self._build_context_dir)

    def __del__(self):
        """Destruction of `DockerKernel` instance"""
        try:
            self._tmp_dir.cleanup()
            self.send_response("Temporary directory removed")
        except Exception as e:
            self.send_response(str(e))

    @property
    def kernel_info(self):
        """Extends kernel info of `ipykernel.kernelbase.Kernel`.

        Returns:
            dict[str, Any]: Kernel's information including the current image id.
        """
        info = super().kernel_info
        info["imageId"] = self._sha1
        return info
    
    ########################################
    # Core functionalities
    ########################################

    def do_execute(self, code: str, silent: bool, store_history=True, user_expressions={}, allow_stdin=False):
        """Execute user code.

        #TODO: Remove unused args (all except code)

        Args:
            code (str): The user's code.
            silent (bool): Whether to display output.
            store_history (bool, optional): Whether to record this code in history and increase the execution count.
                If *silent* is `True`, this is implicitly `False`.
                Defaults to `True`.
            user_expressions (dict, optional): Mapping of names to expressions to evaluate after the code has run.
                You can ignore this if you need to.
                Defaults to `{}`.
            allow_stdin (bool, optional): Whether the frontend can provide input on request (e.g. for Python's `raw_input()`).
                Defaults to `False`.

        Returns:
            dict: Specified [here](https://jupyter-client.readthedocs.io/en/stable/messaging.html#execution-results)
        """
        
        ####################
        # Prepare kernel for code execution
        self.reset_payload()
        self._frontend = self._frontend if self._frontend is not None else FrontendInteraction(JupyterFrontEnd())

        ####################
        # Magic execution
        try:
            MagicClass, args, flags = Magic.detect_magic(code)

            if MagicClass is not None:
                MagicClass(self, *args, **flags).call_magic()
                #TODO: Use payload getter
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        except MagicError as e:
            self.send_response(str(e))
            return {'status': 'error', "ename": "MagicError", "evalue": str(e), "traceback": []}

        ####################
        # Frontend execution
        frontend_interacted = self._frontend.handle_code(code)
        if frontend_interacted:
            return {'status': 'error', "ename": "FrontEndExecuted", "evalue": "", "traceback": []}
        # Show build context warning once
        if self._build_context_dir is None and not self._build_context_warning_shown:
            self._frontend.build_context_warning()
            self._build_context_warning_shown = True

        ####################
        # Docker execution
        self.build_image(code)
        #TODO: Remove commented code
        # self.send_response(f"temp dir:{self._tmp_dir.name}\n")
        #TODO: Use payload getter
        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}

    def create_build_stage(self, code: str):
        """Add current `_sha1` to the code.

        Replace alias or index provided in *code* with image id.

        Args:
            code (str): The user's code.

        Returns:
            str: User code with added `_sha1`
        """
        code = self._replace_alias(code)
        if self._sha1 is not None:
            code = f"FROM {self._sha1}\n{code}"
        return code

    ########################################
    # Notebook interaction
    ########################################

    def send_response(self, content_text: str, stream=None, msg_or_type="stream", content_name="stdout"):
        """Send a response to the message currently processed.

        #TODO: Remove unused args (all except content_text)

        Args:
            content_text (str): Message to be displayed.
        """
        stream = self.iopub_socket if stream is None else stream
        super().send_response(stream, msg_or_type, {"name": content_name, "text": content_text})

    @property
    def payload(self) -> list[dict[str, str]]:
        return self._payload

    @payload.setter
    def payload(self, payload: tuple[str, str, bool]):
        """Payload that can trigger frontend actions.

        #! **Depreciated** though [no replacement](https://jupyter-client.readthedocs.io/en/stable/messaging.html#payloads-deprecated) available yet

        #TODO: Turn *payload* into `dict` or reference each key/value on their own

        Args:
            payload (tuple[str, str, bool]): Payload to be send to the frontend.
        """
        self._payload = [{
            "source": payload[0],
            "text": payload[1],
            "replace": payload[2],
        }]

    def reset_payload(self):
        """Resets payload"""
        self._payload = []

    def do_complete(self, code: str, cursor_pos: int):
        """Provide code completion.

        Args:
            code (str): The user's code.
            cursor_pos (int): The cursor's position in *code*. This is where the completion is requested.

        Returns:
            dict[str, Any]: A dictionary including all *matches* to be shown as autocompletion.
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
        """Tag an image.

        #TODO: Remove MagicError here. It's only supposed to be used in Magics
        #TODO: Better Exception handling

        Args:
            name (str): The image name to be assigned.
            tag (str | None, optional): Typically a specific version or variant of an image.
                If tag is `None` is given, a default one (*latest*) is assigned by the *docker daemon*
                Defaults to `None`.

        Raises:
            MagicError: To be replaced.
            MagicError: To be replaced.
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

    def build_image(self, code:str):
        """Build docker image by passing input to the docker API.

        Args:
            code (str): The user's code.
        """
        tmp_dir = self._tmp_dir.name
        build_code = self.create_build_stage(code)
        dockerfile_path = create_dockerfile(build_code, tmp_dir)

        try:
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
        except APIError as e:
            if e.explanation is not None:
                self.send_response(str(e.explanation))
            else:
                self.send_response(str(e))
            return
        self._save_build_stage(code, self._sha1)

    def _save_build_stage(self, code:str, image_id:str):
        """Save build stage with an index and - if provided - an alias.

        Args:
            code (str): The user's code.
            image_id (str): The build's image id.
        """
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

    def _replace_alias(self, code: str):
        """Replace an image index or alias with the locally stored image id.

        Args:
            code (str): The user's code.

        Returns:
            str: The user's code with the image index or alias replaced.
        """
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
        """Getter for current build arguments.

        Returns:
            dict[str, str]: _description_
        """
        return self._buildargs

    @buildargs.setter
    def buildargs(self, buildargs: dict[str, str]):
        """Setter for current build arguments.

        #TODO: Change this to be an actual setter. Implement an update function instead.

        Args:
            buildargs (dict[str, str]): Build arguments that are to be updated.
        """
        self._buildargs.update(buildargs)

    def remove_buildargs(self, all: bool=False, *names: str):
        """Remove current build arguments specified by name (or all).

        #TODO: Remove unnecessary *all*, just remove all if no names are given

        Args:
            all (bool, optional): Determines if all *buildargs* should be removed.
                Defaults to `False`.
            *names (tuple[str, ...]): Names of build arguments to be removed.
        """
        if all:
            self._buildargs = {}
        else:
            self.send_response(names)
            for name in names:
                self.buildargs.pop(name)

    def change_build_context_directory(self, source_dir: str):
        """Change the build context that is used by Docker.

        Args:
            source_dir (str): The path of the new build context directory.
        """
        self._build_context_dir = source_dir

        empty_response = empty_dir(self._tmp_dir.name)
        if empty_response:
            self.send_response("Temporary directory emptied\n")
        else:
            self.send_response(str(empty_response))
            return
        
        # Leave temp directory empty if no build context is available
        # This is used primarily when the inital directory is too large
        if not self._build_context_dir:
            return
        docker_ignore_rules = preporcessed_dockerignore(self._build_context_dir)
        ignore_function = dockerignore(self._build_context_dir, docker_ignore_rules)
        copy_response = copy_files(self._build_context_dir, self._tmp_dir.name, ignore=ignore_function)
        if copy_response:
            self.send_response("Build context changed\n")
        else:
            self.send_response(str(copy_response))

            return

    def get_stages(self):
        table = PrettyTable(["index", "alias", "image id"])
        for index, _rest in self._build_stage_indices.items():
            table.add_row([index, _rest[1], _rest[0]])
        return table
