import { JupyterFrontEnd } from '@jupyterlab/application';
import { showDialog } from '@jupyterlab/apputils';

export const addCommand = (app: JupyterFrontEnd) => {
  const command = 'docker:context_warning';
  const { commands } = app;

  commands.addCommand(command, {
    label: 'Choose build context',
    caption: 'Choose build context',
    execute: async () => {
      await showDialog({
        title: 'No build context set',
        body: 'The size of the current working directory is large. To prevent long initial loading times, no build context was set. Please manually set the context with the context magic "%context /your/custom/path"',
        buttons: [],
        hasClose: true
      });
    }
  });
};
