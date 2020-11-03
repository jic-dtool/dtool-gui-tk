"""Tkinter GUI code."""


import os
import sys
import logging

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter.font import nametofont

from dtool_gui.models import (
    LocalBaseURIModel,
    DataSetListModel,
    DataSetModel,
    UnsupportedTypeError,
)

logger = logging.getLogger(__file__)

HOME_DIR = os.path.expanduser("~")


class DataSetListFrame(ttk.Frame):
    """List dataset frame."""

    def __init__(self, master, root):
        super().__init__(master)
        logger.info("Initialising {}".format(self))

        # Make sure that the GUI expands/shrinks when the window is resized.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.root = root
        self.columns = ("name", "size_str", "num_items", "creator", "date")
        self.dataset_list = ttk.Treeview(
            self,
            show="headings",
            height=10,
            selectmode="browse",
            columns=self.columns
        )
        self.dataset_list.heading("name", text="Dataset name")
        self.dataset_list.heading("size_str", text="Size")
        self.dataset_list.heading("num_items", text="Num items")
        self.dataset_list.heading("creator", text="Creator")
        self.dataset_list.heading("date", text="Date")
        self.dataset_list.column("size_str", width=80, anchor="e")
        self.dataset_list.column("num_items", width=80, anchor="e")
        self.dataset_list.column("creator", width=80, anchor="w")
        self.dataset_list.column("date", width=80, anchor="w")

        # Add a scrollbar.
        yscrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.dataset_list.yview
        )
        self.dataset_list.configure(yscroll=yscrollbar.set)

        # Bind event when row is selected.
        self.dataset_list.bind(
            "<<TreeviewSelect>>",
            self.update_selected_dataset
        )

        # Layout the fame.
        self.dataset_list.grid(row=0, column=0, sticky="nswe")
        yscrollbar.grid(row=0, column=1, sticky="ns")

        self.refresh()

    def update_selected_dataset(self, event):
        selected = self.dataset_list.selection()[0]
        index = self.dataset_list.index(selected)
        dataset_uri = self.root.dataset_list_model.get_uri(index)
        self.root.load_dataset(dataset_uri)
        self.root.dataset_frame.refresh()

    def refresh(self):
        """Refreshing list dataset frame."""
        logger.info("Refreshing {}".format(self))
        self.dataset_list.delete(*self.dataset_list.get_children())
        self.root.dataset_list_model.reindex()
        for props in self.root.dataset_list_model.yield_properties():
            values = [props[c] for c in self.columns]
            self.dataset_list.insert("", "end", values=values)
            logger.info("Loaded dataset: {}".format(props["name"]))
        if len(self.root.dataset_list_model.names) > 0:
            dataset_uri = self.root.dataset_list_model.get_uri(0)
            self.root.load_dataset(dataset_uri)
        else:
            self.root.dataset_model.clear()


class DataSetFrame(ttk.Frame):
    """View dataset frame."""

    def __init__(self, master, root):
        super().__init__(master)
        logger.info("Initialising {}".format(self))

        # Make sure that the GUI expands/shrinks when the window is resized.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.root = root
        if self.root.base_uri_model.get_base_uri() is not None:
            self.refresh()

    def refresh(self):
        """Refreshing dataset frame."""
        logger.info("Refreshing {}".format(self))
        for widget in self.winfo_children():
            logger.info("Destroying widget: {}".format(widget))
            widget.destroy()

        # Skip if a dataset is not loaded.
        if self.root.dataset_model.name is None:
            return

        # Display the name.
        heading_font = nametofont("TkHeadingFont")
        name = ttk.Label(self, text=self.root.dataset_model.name, font=heading_font)  # NOQA
        name.grid(row=0, column=0, columnspan=2, sticky="nw")
        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.grid(row=1, column=0, columnspan=2, sticky="ew")

        if self.root.dataset_model.metadata_model is None:
            ttk.Label(self, text="Dataset contains unsupported metadata types").grid(row=1, column=0, columnspan=2, sticky="ew")  # NOQA

        else:
            for i, name in enumerate(self.root.dataset_model.metadata_model.in_scope_item_names):  # NOQA
                value = self.root.dataset_model.metadata_model.get_value(name)
                value_as_str = str(value)
                row = i + 2
                ttk.Label(self, text=name).grid(row=row, column=0, sticky="ne")  # NOQA
                entry = ttk.Entry(self, width=50)
                entry.insert(0, value_as_str)
                entry.configure(state="readonly")
                entry.grid(row=row, column=1, sticky="nw")  # NOQA


class PreferencesWindow(tk.Toplevel):
    """Preferences window."""

    def __init__(self, master):
        super().__init__(master)
        logger.info("Initialising {}".format(self))
        self.root = master
        mainframe = ttk.Frame(self)
        mainframe.grid(row=0, column=0, sticky="nwes")
        label_frame = ttk.LabelFrame(mainframe, text="Local base URI directory")  # NOQA
        label_frame.grid(row=0, column=0,)
        self.local_base_uri_directory = tk.StringVar()
        self.local_base_uri_directory.set(
            self.root.base_uri_model.get_base_uri()
        )
        label = ttk.Label(label_frame, textvar=self.local_base_uri_directory)
        button = ttk.Button(
            label_frame,
            text="Select local base URI directory",
            command=self.select_local_base_uri_directory
        )
        label.grid(row=0, column=0)
        button.grid(row=1, column=0)

    def select_local_base_uri_directory(self):
        base_uri_directory = fd.askdirectory(
            title="Select data directory",
            initialdir=HOME_DIR
        )
        self.root.base_uri_model.put_base_uri(base_uri_directory)
        self.local_base_uri_directory.set(base_uri_directory)
        logger.info(
            "Local base URI directory set to: {}".format(
                base_uri_directory
            )
        )
        self.root.refresh()


class App(tk.Tk):
    """Root tkinter application."""

    def __init__(self):
        super().__init__()
        logger.info("Initialising dtool-gui")

        # Make sure that the GUI expands/shrinks when the window is resized.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Initialise the models.
        self.base_uri_model = LocalBaseURIModel()
        self.dataset_list_model = DataSetListModel()
        self.dataset_model = DataSetModel()

        # Configure the models.
        self.dataset_list_model.set_base_uri_model(self.base_uri_model)
        if len(self.dataset_list_model.names) > 0:
            first_uri = self.dataset_list_model.get_uri(0)
            self.load_dataset(first_uri)

        # Determine the platform.
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

        # Add content to the menus.
        self._add_menu_command(
            menu=menu_file,
            label="New file...",
            accelerator_key="N",
            cmd=self.new_dataset,
            event_cmd=self._new_dataset_event
        )

        if self.platform != "aqua":
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

        if self.platform != "aqua":
            self._add_menu_command(
                menu=menu_edit,
                label="Edit preferences...",
                accelerator_key="P",
                cmd=self.show_perferences_window,
                event_cmd=self._show_perferences_window_event
            )

        # Deal with preferences menu item on Mac.
        self.createcommand("tk::mac::ShowPreferences", self.show_perferences_window)  # NOQAQ

        self.config(menu=menubar)

        self.mainframe = ttk.Frame(self)
        self.mainframe.grid(row=0, column=0, sticky="nwes")

        # Make sure that the GUI expands/shrinks when the window is resized.
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.dataset_list_frame = DataSetListFrame(self.mainframe, self)
        self.dataset_list_frame.grid(row=0, column=0, sticky="nsew")

        self.dataset_frame = DataSetFrame(self.mainframe, self)
        self.dataset_frame.grid(row=0, column=1, sticky="new")

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

    def _show_perferences_window_event(self, event):
        self.show_perferences_window()

    def show_perferences_window(self):
        """Show the preferences window."""
        logger.info(self.show_perferences_window.__doc__)
        PreferencesWindow(self)

    def load_dataset(self, dataset_uri):
        """Load dataset and deal with UnsupportedTypeError exceptions."""
        try:
            self.dataset_model.load_dataset(dataset_uri)
        except UnsupportedTypeError:
            logging.warning("Dataset contains unsupported metadata type")

    def refresh(self):
        """Refreshing all frames."""
        logger.info(self.refresh.__doc__)
        self.dataset_list_frame.refresh()
        self.dataset_frame.refresh()


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
