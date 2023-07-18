import shutil
import tempfile

import docker
import io
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
        self._index_to_image_id = {}
        self._alias_to_index = {}
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
            code = self.create_build_stage(code)
            self.build_image(code)
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
        code = self.replace_base_image_with_id(code)
        if self._sha1 is not None:
            code = f"FROM {self._sha1}\n{code}"
        return code

    def replace_base_image_with_id(self, code):
        code_seg = code.lower().strip().split(" ")

        try:
            contain_image = next(x for x in code_seg if x.startswith('--from'))
        except StopIteration:
            return code
        image_alias = ''.join(contain_image).split("=")[1]
        try:
            if image_alias.isdigit():
                base_image_id = self._index_to_image_id[int(image_alias)]
            else:
                base_image_id = self._index_to_image_id[self._alias_to_index[image_alias]]
        except KeyError or IndexError:
            self.send_response("Can't find the base image")
        code = f"{code_seg[0]} --from={base_image_id} {' '.join(code_seg[2:])}"
        return code

    def start_a_new_layer(self, code):
        if code.lower().strip().startswith('from'):
            try:
                _from, *remain = code.split(' ')
            except ValueError:
                pass
            # index = len(self._index_to_image_id)
            if type(self._current_alias) is int:
                index = self._current_alias + 1
            elif type(self._current_alias) is str:
                index = self._alias_to_index[self._current_alias] + 1
            else:
                index = 0
            if len(remain) > 1 and remain[1] == 'as':
                alias = remain[2]
                self._alias_to_index[alias] = index
            else:
                alias = index
            self._index_to_image_id[index] = None
            self._current_alias = alias

    def build_image(self, code):
        """ Build docker image by passing input to the docker API."""

        f = io.BytesIO(code.encode('utf-8'))
        logs = []
        tmp_dir = tempfile.mkdtemp()
        try:
            self.copy_cwd_to_tmp_dir(tmp_dir)
            dockerfile_path = self.create_dockerfile(code, tmp_dir)
        except Exception as e:
            self.send_response(str(e))

        self.start_a_new_layer(code)
        for logline in self._api.build(path=tmp_dir,dockerfile=dockerfile_path, rm=True):
            loginfo = json.loads(logline.decode())
            if 'error' in loginfo:
                self.send_response(f'error:{loginfo["error"]}\n')
                self.delete_current_stage()
            if 'aux' in loginfo:
                self._sha1 = loginfo['aux']['ID']
            if 'stream' in loginfo:
                log = loginfo['stream']
                if log.strip() != "":
                    self.send_response(log)
        self.save_current_stage()
        shutil.rmtree(tmp_dir)

    def copy_cwd_to_tmp_dir(self, tmp_dir):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
            shutil.copytree(os.getcwd(), tmp_dir)

    def create_dockerfile(self, code, tmp_dir):
        dockerfile_path = os.path.join(tmp_dir, 'Dockerfile')
        dockerfile = open(dockerfile_path, 'w+')
        dockerfile.write(code)
        dockerfile.close()
        return dockerfile_path

    def save_current_stage(self):
        image_id = self._sha1.split(':')[1][:12]
        if type(self._current_alias) is int:
            self._index_to_image_id[self._current_alias] = image_id
        else:
            self._index_to_image_id[self._alias_to_index[self._current_alias]] = image_id

    def delete_current_stage(self):
        if type(self._current_alias) is int:
            del self._index_to_image_id[self._current_alias]
        else:
            del self._index_to_image_id[self._alias_to_index[self._current_alias]]
            del self._alias_to_index[self._current_alias]
        last_stage_index = list(self._index_to_image_id.keys())[-1]
        last_stage_alias = ''.join({i for i in self._alias_to_index if self._alias_to_index[i] == last_stage_index})
        # self.send_response(f'last_stage_index:{last_stage_index}')
        # self.send_response(f'last_stage_alias:{last_stage_alias}')
        if not last_stage_alias:
            self._current_alias = last_stage_index
        else:
            self._current_alias = last_stage_alias

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


