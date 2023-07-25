import { JupyterFrontEnd } from '@jupyterlab/application';

import { MainAreaWidget, IFrame } from '@jupyterlab/apputils';

export const addCommand = (app: JupyterFrontEnd) => {
  const command: string = 'helper:open';
  let widget = newWidget();

  app.commands.addCommand(command, {
    execute: async ({ hook }) => {
      // Regenerate the widget if disposed
      if (widget.isDisposed) {
        widget = newWidget();
      }
      hook = hook ? '/#' + hook : '';
      widget.content.url =
        'https://docs.docker.com/engine/reference/builder' + hook.toLowerCase();

      if (!widget.isAttached) {
        // Attach the widget to the main work area if it's not there
        app.shell.add(widget, 'main', { mode: 'split-right' });
      }
      // Activate the widget
      app.shell.activateById(widget.id);
    }
  });
};

const newWidget = () => {
  const content = new IFrame();
  const widget = new MainAreaWidget({ content });
  widget.id = 'docker-help';
  widget.title.label = 'Docker Help';
  widget.title.closable = true;
  return widget;
};
