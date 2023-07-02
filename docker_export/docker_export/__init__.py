import os
import os.path

from nbconvert.exporters import TemplateExporter

class DockerExporter(TemplateExporter):
    """
    Dockerfile exporter
    """
    export_from_notebook = "Dockerfile"

    def _file_extension_default(self):
        """
        Dockerfiles have no extension
        """
        return ".Dockerfile"

    @property
    def template_paths(self):
        return super()._template_paths() + [os.path.join(os.path.dirname(__file__), "templates")]

    def _template_file_default(self):
        return "docker_template.tpl"