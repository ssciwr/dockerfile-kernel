import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget, IFrame } from '@jupyterlab/apputils';

/**
 * Initialization data for the helper_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'helper_extension:plugin',
  description: 'Show Docker help in its own tab.',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('JupyterLab extension helper_extension is activated!');

    const newWidget = () => {
      const content = new IFrame();
      const widget = new MainAreaWidget({ content });
      widget.id = 'docker-help';
      widget.title.label = 'Docker Help';
      widget.title.closable = true;
      return widget;
    };
    let widget = newWidget();

    const command: string = 'helper:open';
    app.commands.addCommand(command, {
      label: 'Open Docker Helper',
      execute: async ({ hook }) => {
        // Regenerate the widget if disposed
        if (widget.isDisposed) {
          widget = newWidget();
        }
        hook = hook ? '/#' + hook : '';
        widget.content.url =
          'https://docs.docker.com/engine/reference/builder' +
          hook.toLowerCase();

        if (!widget.isAttached) {
          // Attach the widget to the main work area if it's not there
          app.shell.add(widget, 'main', { mode: 'split-right' });
        }
        // Activate the widget
        app.shell.activateById(widget.id);
      }
    });

    // Add the command to the palette.
    palette.addItem({ command, category: 'Docker' });
  }
};

export default plugin;
