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
        super().__init__(**kwargs)
        self._api = docker.APIClient(base_url='unix://var/run/docker.sock')
        self._sha1 = None
        self._payload = []

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        magic, arguments = detect_magic(code)
        if magic is not None:
            response = call_magic(self, magic, arguments)
            self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": response})
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': self._payload, 'user_expression': {}}
        code = self.create_build_stage(code)
        logs = self.build_image(code)
        for log in logs:
            self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": log})

        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expression': {}}

    def create_build_stage(self, code):
        if self._sha1 is not None:
            code = f"FROM {self._sha1}\n{code}"
        return code

    def build_image(self, code): 
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
    
    def set_payload(self, source, text):
        self._payload = [{
                "source": source,
                # the text contents of the cell to create
                "text": text,
                # If true, replace the current cell in document UIs instead of inserting
                # a cell. Ignored in console UIs.
                "replace": True,
            }
        ]
                    

