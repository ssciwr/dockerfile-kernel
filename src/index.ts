import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { addCommand as addHelperCommand } from './helper/index';
import { addCommand as addImportCommand } from './import/index';
import { addCommand as addShellCommand } from './shell/index';
import { addCommand as addBuildContextCommand } from './build_context/index';
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
  addBuildContextCommand(app);
};

/**
 * Initialization data for the dockerfile_kernel extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'dockerfile_kernel:plugin',
  description: 'A Dockerfile kernel for JupyterLab',
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
