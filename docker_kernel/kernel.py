import docker
import io
import json


from ipykernel.kernelbase import Kernel

# The single source of version truth
__version__ = "0.0.1"

class DockerKernel(Kernel):
    implementation = None
    implementation_version = __version__
    language = 'docker'
    language_version = docker.__version__
    language_info = {
        "name": 'docker',
        'mimetype': 'text/x-dockerfile-config',
        'file_extension': ".dockerfile"
    }
    banner = "Dockerfile Kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._api = docker.APIClient(base_url='unix://var/run/docker.sock')
        self._sha1 = None
        self._in_shell = False
        self._container = None
        self._workdir = "/"

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if (code.lstrip().startswith("%shell")):
            if not self._sha1:
                self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": "There is no docker image present!"})
            else:
                self._create_container(self._sha1)
                self._in_shell = True
                self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": "You are now accessing the shell of a docker container created by the current image..."})
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expression': {}}

        if (code.lstrip().startswith("%exit")):
            self._in_shell = False
            self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": "Shell disabled..."})
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expression': {}}
        
        if self._in_shell:
            self._execute_command(code)
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
    
    def _create_container(self, image_id):
        # TODO: Error handling
        self._container = self._api.create_container(image_id, command="sleep infinity")
        self._api.start(container=self._container)
        self._workdir = "/"

    def _execute_command(self, command):
        bash_command = f"bash -c '{command}'"
        exec_info = self._api.exec_create(container=self._container.get('Id'), cmd=bash_command, workdir=self._workdir)
        response = self._api.exec_start(exec_id=exec_info.get('Id')).decode()
        self._handle_cd_command(command, response)
        self.send_response(self.iopub_socket, 'stream', {"name": "stdout", "text": f"{response}"})

    def _handle_cd_command(self, command, response):
        if "No such file or directory" in response:
            return
        command = command.strip()
        if not command.startswith("cd"):
            return
        if command.startswith("cd /"):
            self._workdir = command.split(" ")[1]
        else:
            if not self._workdir.endswith("/"):
                self._workdir += "/"
            self._workdir += command.split(" ")[1]

