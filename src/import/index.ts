import { JupyterFrontEnd } from '@jupyterlab/application';
import {
  InputDialog,
  showErrorMessage,
  ICommandPalette
} from '@jupyterlab/apputils';
import { URLExt } from '@jupyterlab/coreutils';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { ServerConnection } from '@jupyterlab/services';
import { CommandRegistry } from '@lumino/commands';

import { UUID, ReadonlyPartialJSONObject } from '@lumino/coreutils';

import { Content } from './types';

export const addCommand = (
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  fileBrowser: IDefaultFileBrowser
) => {
  const command = 'docker:import';
  const { commands } = app;

  commands.addCommand(command, {
    label: 'Open Dockerfile from Path…',
    caption: 'Open Dockerfile from path',
    execute: async args => {
      const path = await getDockerfilePath(fileBrowser, commands, args);

      if (typeof path !== 'string') {
        return;
      }

      // Check path for dockerfile
      if (!path.toLowerCase().endsWith('dockerfile')) {
        return showErrorMessage(
          'Not a Dockerfile',
          "File must have extension 'Dockerfile'"
        );
      }

      // Read Dockerfile
      const response = await ServerConnection.makeRequest(
        URLExt.join(
          app.serviceManager.serverSettings.baseUrl,
          'api/contents',
          path
        ),
        {},
        app.serviceManager.serverSettings
      );
      const file = await response.json();
      const cells = getFileCells(file);
      const content = createNotebookJSON(cells);

      // Write and open Jupyter Notebook
      const newPath = path + '.ipynb';

      await app.serviceManager.contents.save(newPath, {
        type: 'file',
        format: 'text',
        content: JSON.stringify(content)
      });

      commands.execute('docmanager:open', {
        path: newPath
      });
    }
  });
};

const getDockerfilePath = async (
  fileBrowser: IDefaultFileBrowser,
  commands: CommandRegistry,
  args: ReadonlyPartialJSONObject
) => {
  let path: string | undefined;
  if (args?.path) {
    path = args.path as string;
  } else {
    path =
      (
        await InputDialog.getText({
          label: 'Path',
          placeholder: '/path/relative/to/jlab/root',
          title: 'Open Dockerfile Path',
          okLabel: 'Open'
        })
      ).value ?? undefined;
  }
  if (!path) {
    return;
  }
  try {
    const trailingSlash = path !== '/' && path.endsWith('/');
    if (trailingSlash) {
      // The normal contents service errors on paths ending in slash
      path = path.slice(0, path.length - 1);
    }
    const { services } = fileBrowser.model.manager;
    const item = await services.contents.get(path, {
      content: false
    });
    if (trailingSlash && item.type !== 'directory') {
      throw new Error(`Path ${path}/ is not a directory`);
    }
    await commands.execute('filebrowser:go-to-path', {
      path,
      dontShowBrowser: args.dontShowBrowser
    });
    if (item.type === 'directory') {
      return;
    }
  } catch (reason: any) {
    if (reason.response && reason.response.status === 404) {
      reason.message = `Could not find path: %1 ${path}`;
    }
    return showErrorMessage('Cannot open', reason);
  }
  return path;
};

const getFileCells = (file: any) => {
  const cells: string[] = [];
  const codeBlocks: string = file.content.split('\n#cellEnd');
  for (const block of codeBlocks) {
    const codeCells = block.split('#cellStart\n');
    for (const cell of codeCells) {
      // Cell is not multiline cell with empty lines
      if (cell.startsWith('\n') || cell.endsWith('\n')) {
        cells.push(...cell.split('\n\n').filter(cell => cell.length > 0));
      } else {
        // Cell can be an empty string if cellStart was the first or cellEnd the last line in the Dockerfile
        if (cell !== '') {
          cells.push(cell);
        }
      }
    }
  }
  return cells;
};

const createNotebookJSON = (cells: string[]) => {
  // Create notebook json

  const content: Content = {
    cells: [],
    metadata: {
      kernelspec: {
        display_name: 'Dockerfile',
        language: 'text',
        name: 'docker'
      },
      language_info: {
        file_extension: '.dockerfile',
        mimetype: 'text/x-dockerfile-config',
        name: 'docker'
      }
    },
    nbformat: 4,
    nbformat_minor: 5
  };

  const markdownComment = '#md ';
  const magicComment = '#mg ';
  for (const cell of cells) {
    const editedCell: string[] = [];
    let cellType = 'code';
    for (let line of cell.split('\n')) {
      if (line.startsWith(markdownComment)) {
        line = line.substring(markdownComment.length);
        cellType = 'markdown';
      } else if (line.startsWith(magicComment)) {
        line = line.substring(magicComment.length);
      }
      editedCell.push(line + '\n');
    }

    let lastLine = editedCell.pop();
    lastLine = lastLine?.substring(0, lastLine.length - 1);
    if (lastLine !== undefined) {
      editedCell.push(lastLine);
    }

    content.cells.push({
      cell_type: cellType,
      execution_count: null,
      id: UUID.uuid4(),
      metadata: {},
      outputs: [],
      source: editedCell
    });
  }
  return content;
};
