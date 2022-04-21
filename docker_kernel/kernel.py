import docker
import io
import json


from ipykernel.kernelbase import Kernel


class DockerKernel(Kernel):
    implementation = None
    implementation_version = '1.0'
    language = 'docker'
    language_version = '1.0'
    language_info = {
        "name": 'Docker',
        'mimetype': 'text/plain',
        'file_extension': ".dockerfile"
    }
    banner = "Dockerfile Kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._api = docker.APIClient(base_url='unix://var/run/docker.sock')
        self._sha1 = None

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
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
