import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { addCommand as addHelperCommand } from './helper/index';
import { addCommand as addImportCommand } from './import/index';
import { addCommand as addShellCommand } from './shell/index';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { ICommandPalette } from '@jupyterlab/apputils';

const addCommands = (
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  fileBrowser: IDefaultFileBrowser
) => {
  addHelperCommand(app);
  addImportCommand(app, palette, fileBrowser);
  addShellCommand(app);
};

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'docker_extension:plugin',
  description: 'Multiple frontend features for the docker kernel',
  autoStart: true,
  requires: [ICommandPalette, IDefaultFileBrowser],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    fileBrowser: IDefaultFileBrowser
  ) => {
    addCommands(app, palette, fileBrowser);
  }
};

export default plugin;
