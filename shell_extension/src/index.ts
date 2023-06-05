import { IDisposable, DisposableDelegate } from '@lumino/disposable';

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ToolbarButton } from '@jupyterlab/apputils';

import { DocumentRegistry } from '@jupyterlab/docregistry';

import {
  NotebookPanel,
  INotebookModel
} from '@jupyterlab/notebook';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'toolbar-shell-button',
  autoStart: true,
};

/**
 * A notebook widget extension that adds a button to the toolbar.
 */
export class ButtonExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  public app: JupyterFrontEnd<JupyterFrontEnd.IShell, 'desktop' | 'mobile'> | undefined = undefined;
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
  createNew(
    panel: NotebookPanel
  ): IDisposable {
    const createConsole = () => {
        this.app?.commands.execute('notebook:create-console');
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
  app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension({app: app}));
}

/**
 * Export the plugin as default.
 */
export default plugin;
