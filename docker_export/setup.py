from setuptools import setup

setup(
    entry_points = {
        'nbconvert.exporters': [
            'docker = docker_export:DockerExporter',
        ],
    },
    package_data={'docker_export': ['templates/*.tpl']}
)