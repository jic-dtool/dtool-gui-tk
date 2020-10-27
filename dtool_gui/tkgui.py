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

        self.title("dtool-gui")

        # Remove ability to tear off menu on Windows and X11.
        self.option_add("*tearOff", False)

        # Create the menubar.
        menubar = tk.Menu(self)

        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label="File")
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_edit, label="Edit")

        menu_file.add_command(
            label="New dataset...",
            accelerator="Ctrl+N",
            command=self.new_dataset
        )
        menu_file.add_separator()
        menu_file.add_command(
            label="Quit",
            accelerator="Ctrl+Q",
            command=self.quit
        )
        menu_edit.add_command(
            label="Edit metadata...",
            accelerator="Ctrl+M",
            command=self.edit_metadata
        )

        self.config(menu=menubar)

        # Bind the accelerator keys.
        self.bind_all("<Control-q>", self._quit_event)
        self.bind_all("<Control-n>", self._new_dataset_event)
        self.bind_all("<Control-m>", self._edit_metadata)

    def _new_dataset_event(self, event):
        self.new_dataset()

    def new_dataset(self):
        """Open window with form to create a new dataset."""
        logger.info(self.new_dataset.__doc__)

    def _edit_metadata(self, event):
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
