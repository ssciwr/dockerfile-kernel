import uuid
import json
import os

def convertDockerfileToNotebook(path_to_dockerfile):
    with open(path_to_dockerfile, "r", newline="\n") as dockerfile:
        lines = dockerfile.readlines()
        lines = [line.rstrip("\n") for line in lines]
        lines = "\n".join(lines).split("\n\n")
        content = {
          "cells": [],
          "metadata": {
            "kernelspec": {
              "display_name": 'Dockerfile',
              "language": 'text',
              "name": 'docker'
            },
            "language_info": {
              "file_extension": '.dockerfile',
              "mimetype": 'text/x-dockerfile-config',
              "name": 'docker'
            }
          },
          "nbformat": 4,
          "nbformat_minor": 5
        };

    for line in lines:
        cell_type = "code";
        if line.startswith("# "):
            line = line[2:]
            if not line.startswith("%"):
                cell_type = "markdown"
        content["cells"].append({
            "cell_type": cell_type,
            "execution_count": None,
            "id": str(uuid.uuid4()),
            "metadata": {},
            "outputs": [],
            "source": line
        })
    
    notebook_string = json.dumps(content)
    with open(f"{os.path.dirname(path_to_dockerfile)}/Test.ipynb", "w") as dockerfile:
        dockerfile.write(notebook_string)
      
    return notebook_string