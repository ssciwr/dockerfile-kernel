import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import { JupyterFrontEnd } from '@jupyterlab/application';
import {
  ToolbarButton,
  MainAreaWidget,
  InputDialog
} from '@jupyterlab/apputils';
import { ITerminal } from '@jupyterlab/terminal';
import { NotebookPanel } from '@jupyterlab/notebook';
import {
  ITerminalConnection,
  ConnectionStatus
} from '@jupyterlab/services/lib/terminal/terminal';

export const addCommand = (app: JupyterFrontEnd) => {
  app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension(app));
};

export class ButtonExtension {
  readonly app: JupyterFrontEnd<JupyterFrontEnd.IShell, 'desktop' | 'mobile'>;
  currentImage: string | null;

  public constructor(
    app: JupyterFrontEnd<JupyterFrontEnd.IShell, 'desktop' | 'mobile'>
  ) {
    this.app = app;
    this.currentImage = null;
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
      const kernelInfo =
        await panel.sessionContext.session?.kernel?.requestKernelInfo();
      const kernelName = panel.sessionContext.session?.kernel?.name;

      // If the notebook's kernel is not the Docker kernel, don't add specific code
      if (kernelName !== 'docker') {
        return;
      }

      // If no image Id is provided by the Docker kernel, don't add specific code
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore - Due to custom Kernel info in Docker Kernel
      if (kernelInfo === undefined || kernelInfo.content.imageId === null) {
        return;
      }
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore - Due to custom Kernel info in Docker Kernel
      this.currentImage = kernelInfo.content.imageId;

      InputDialog.getText({
        title: "Console's Initial Command",
        text: `docker run -it -w /root ${this.currentImage}`
      }).then(value => {
        if (value.value === null) {
          return;
        }
        const command = value.value + '\r';
        this.app.commands
          .execute('terminal:create-new')
          .then((widget: MainAreaWidget<ITerminal.ITerminal>) => {
            const sendInitialCommand = (
              session: ITerminalConnection,
              status: ConnectionStatus
            ) => {
              if (status === 'connected' && this.currentImage !== null) {
                session.send({
                  type: 'stdin',
                  content: [command]
                });
              }
            };

            widget.content.session.connectionStatusChanged.connect(
              sendInitialCommand
            );
          });
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
