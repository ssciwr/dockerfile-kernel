from setuptools import setup

setup(
    entry_points = {
        'nbconvert.exporters': [
            'dockerfile = docker_export:DockerExporter',
        ],
    },
    package_data={'docker_export': ['templates/*.tpl']}
)