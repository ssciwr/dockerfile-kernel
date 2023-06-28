import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, InputDialog, showErrorMessage } from '@jupyterlab/apputils';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';


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
    fileBrowser: IDefaultFileBrowser,
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
        console.log(lines);

        // commands.execute('docmanager:open', {
        //   path: model.path
        // });
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
