import { IDisposable, DisposableDelegate } from '@lumino/disposable';

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ToolbarButton, MainAreaWidget } from '@jupyterlab/apputils';

import { ITerminal } from '@jupyterlab/terminal';

import { NotebookPanel } from '@jupyterlab/notebook';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'toolbar-shell-button',
  autoStart: true
};

/**
 * A notebook widget extension that adds a button to the toolbar.
 */
export class ButtonExtension {
  public app:
    | JupyterFrontEnd<JupyterFrontEnd.IShell, 'desktop' | 'mobile'>
    | undefined = undefined;
  public constructor(init?: Partial<ButtonExtension>) {
    Object.assign(this, init);
  }

  /**
   * Create a new extension that shows button in the toolbar.
   * The button can be used to create a console instance for the notebook.
   *
   * @param panel Notebook panel
   * @returns Disposable on the added button
   */
  createNew(panel: NotebookPanel): IDisposable {
    const createConsole = async () => {
      if (this.app === undefined) {
        return;
      }

      let reply =
        await panel.sessionContext.session?.kernel?.requestKernelInfo();
      let kernelName = panel.sessionContext.session?.kernel?.name;

      if (reply === undefined) {
        return;
      }

      this.app.commands
        .execute('terminal:create-new')
        .then((widget: MainAreaWidget<ITerminal.ITerminal>) => {
          // If the notebook's kernel is not the Docker kernel, don't add specific code
          if (kernelName !== 'docker') {
            return;
          }

          // If no image Id is provided by the Docker kernel, don't add specific code
          // @ts-ignore - Due to custom Kernel info in Docker Kernel
          if (reply.content.imageId === null) {
            return;
          }

          const terminal = widget.content;
          // TODO: Figure out why it doesnt work on first terminal thats opened
          // ? Is it possible to execute the command after pasting
          terminal.paste(
            // @ts-ignore - Due to custom Kernel info in Docker Kernel
            `docker run -it --entrypoint /bin/bash ${reply?.content.imageId}`
          );
        });
    };
    const button = new ToolbarButton({
      className: 'create-console-button',
      label: 'Create Console',
      onClick: createConsole,
      tooltip: 'Create console for current notebook'
    });

    // 10 is the index in the standard toolbar to correctly place the button
    panel.toolbar.insertItem(10, 'createConsole', button);
    return new DisposableDelegate(() => {
      button.dispose();
    });
  }
}

/**
 * Activate the extension.
 *
 * @param app Main application object
 */
function activate(app: JupyterFrontEnd): void {
  app.docRegistry.addWidgetExtension(
    'Notebook',
    new ButtonExtension({ app: app })
  );
}

/**
 * Export the plugin as default.
 */
export default plugin;
