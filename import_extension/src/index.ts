import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {
  ICommandPalette,
  InputDialog,
  showErrorMessage
} from '@jupyterlab/apputils';
import { URLExt } from '@jupyterlab/coreutils';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { ServerConnection } from '@jupyterlab/services';

import { UUID } from '@lumino/coreutils';

/**
 * Initialization data for the main menu example.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'import_extension:plugin',
  description: 'Minimal JupyterLab example adding a menu.',
  autoStart: true,
  requires: [ICommandPalette, IDefaultFileBrowser],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    fileBrowser: IDefaultFileBrowser
  ) => {
    const { commands } = app;

    // Add a command
    const command = 'docker:import';
    commands.addCommand(command, {
      label: 'Open Dockerfile from Path…',
      caption: 'Open Dockerfile from path',
      execute: async args => {
        // Get Dockerfile path
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
        const lines: string[] = file.content.split('\n\n');

        // Create notebook json
        type Cell = {
          cell_type: string;
          execution_count: number | null;
          id: string;
          metadata: object;
          outputs: object[];
          source: string[];
        };
        type MetaData = {
          kernelspec: {
            display_name: string;
            language: string;
            name: string;
          };
          language_info: {
            file_extension: string;
            mimetype: string;
            name: string;
          };
        };
        type Content = {
          cells: Cell[];
          metadata: MetaData;
          nbformat: number;
          nbformat_minor: number;
        };

        let content: Content = {
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

        const splitLines = (line: string): string[] => {
          line = line.trim()
          let lines = line.split('\n');
          for (var i = 0; i < lines.length-1; i++) {
            lines[i] += "\n"
          }
          return lines
        };

        for (var line of lines) {
          let cellType = 'code';
          if (line.startsWith('# ')) {
            line = line.substring(2);
            if (!line.startsWith("%")){
              cellType = 'markdown';
            }
          }
          content.cells.push({
            cell_type: cellType,
            execution_count: null,
            id: UUID.uuid4(),
            metadata: {},
            outputs: [],
            source: splitLines(line)
          });
        }

        // Write and open Jupyter Notebook
        path += '.ipynb';

        await app.serviceManager.contents.save(path, {
          type: 'file',
          format: 'text',
          content: JSON.stringify(content)
        });

        commands.execute('docmanager:open', {
          path: path
        });
      }
    });

    // Add the command to the command palette
    const category = 'Docker';
    palette.addItem({
      command,
      category,
      args: { origin: 'from the palette' }
    });
  }
};

export default plugin;
