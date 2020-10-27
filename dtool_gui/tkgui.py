"""Tkinter GUI code."""


import os
import sys
import logging

import tkinter as tk

logger = logging.getLogger(__file__)

HOME_DIR = os.path.expanduser("~")


class App(tk.Tk):
    """Root tkinter application."""

    def __init__(self):
        super().__init__()
        logger.info("Initialising dtool-gui")

        self.platform = self.tk.call("tk", "windowingsystem")
        logger.info("Running on platform: {}".format(self.platform))

        self.title("dtool-gui")

        # Remove ability to tear off menu on Windows and X11.
        self.option_add("*tearOff", False)

        # Create the menubar.
        menubar = tk.Menu(self)

        # Make Mac menubar display name of app instead of python.
        if self.platform == "aqua":
            appmenu = tk.Menu(menubar, name="apple")
            menubar.add_cascade(menu=appmenu)
            appmenu.add_command(label="About dtool")
            appmenu.add_separator()

        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label="File")
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_edit, label="Edit")


        self._add_menu_command(
            menu=menu_file,
            label="New file...",
            accelerator_key="N",
            cmd=self.new_dataset,
            event_cmd=self._new_dataset_event
        )
        menu_file.add_separator()
        self._add_menu_command(
            menu=menu_file,
            label="Quit",
            accelerator_key="Q",
            cmd=self.quit,
            event_cmd=self._quit_event
        )
        self._add_menu_command(
            menu=menu_edit,
            label="Edit metadata...",
            accelerator_key="M",
            cmd=self.edit_metadata,
            event_cmd=self._edit_metadata_event
        )

        self.config(menu=menubar)


    def _get_accelerator(self, key):
        key = key.upper()
        if self.platform == "aqua":
            return "Cmd+{}".format(key)
        return "Ctrl+{}".format(key)

    def _get_accelerator_binding(self, key):
        key = key.lower()
        if self.platform == "aqua":
            return "<Command-{}>".format(key)
        return "<Control-{}>".format(key)

    def _add_menu_command(self, menu, label, accelerator_key, cmd, event_cmd):
        menu.add_command(
            label=label,
            accelerator=self._get_accelerator(accelerator_key),
            command=cmd
        )
        self.bind_all(
            self._get_accelerator_binding(accelerator_key),
            event_cmd
        )

    def _new_dataset_event(self, event):
        self.new_dataset()

    def new_dataset(self):
        """Open window with form to create a new dataset."""
        logger.info(self.new_dataset.__doc__)

    def _edit_metadata_event(self, event):
        self.edit_metadata()

    def edit_metadata(self):
        """Open window with form to edit a dataset's metadata."""
        logger.info(self.edit_metadata.__doc__)

    def _quit_event(self, event):
        self.quit()

    def quit(self):
        """Quit the dtool-gui application."""
        logger.info(self.quit.__doc__)


def tkgui(debug_level=logging.WARNING):
    """Start the tkinter app."""
    logging.basicConfig(level=debug_level)
    app = App()
    app.mainloop()


if __name__ == "__main__":
    num_args = len(sys.argv) - 1
    if num_args == 0:
        tkgui()
    if num_args == 1:
        debug_level = sys.argv[1].upper()
        acceptable_debug_levels = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEGUG", "NOTSET")  # NOQA
        if debug_level not in acceptable_debug_levels:
            print("Error: {} not in {}".format(debug_level, acceptable_debug_levels))  # NOQA
            sys.exit(2)
        tkgui(debug_level)
    else:
        print("Error: Too many arguments")
        sys.exit(2)
