import os
import logging

import tkinter as tk
import tkinter.filedialog as fd

import dtoolcore
import dtoolcore.utils
from dtoolcore.utils import DEFAULT_CONFIG_PATH as CONFIG_PATH

logger = logging.getLogger(__file__)

HOME_DIR = os.path.expanduser("~")
JUNK_DIR = os.path.join(HOME_DIR, "junk")


# TODO: this function should probably live in  dtoolcore along with a test.
def iter_datasets_in_base_uri(base_uri):
    """Yield frozen datasets in a base URI."""
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
    StorageBroker = dtoolcore._get_storage_broker(base_uri, CONFIG_PATH)
    for uri in StorageBroker.list_dataset_uris(base_uri, CONFIG_PATH):
        try:
            dataset = dtoolcore.DataSet.from_uri(uri)
            yield dataset
        except dtoolcore.DtoolCoreTypeError:
            pass


class DataSetNameFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        vcmd = (master.register(self.validate_callback), "%P")
        label_frame = tk.LabelFrame(self, text="Dataset name")
        label_frame.pack()
        entry = tk.Entry(
            label_frame,
            validate="key",
            validatecommand=vcmd,
            invalidcommand=self.invalid_name
        )
        entry.pack()

    def validate_callback(self, name):
        if (name is not None) and (len(name) > 0):
            return dtoolcore.utils.name_is_valid(name)
        return True

    def invalid_name(self):
        logger.info("Preventing invalid dataset name creation")


class DataDirectoryFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        label_frame = tk.LabelFrame(self, text="Input data directory")
        label_frame.pack()
        self.entry = tk.Entry(
            label_frame,
        )
        self.btn = tk.Button(
            label_frame,
            text="Select data directory",
            command=self.select_data_directory
        )
        self.entry.pack()
        self.btn.pack()

    def select_data_directory(self):
        data_directory = fd.askdirectory(
            title="Select data directory",
            initialdir=HOME_DIR
        )
        self.entry.delete(0, tk.END)
        self.entry.insert(0, data_directory)
        logger.info(f"Data directory set to: {data_directory}")


class MetaDataFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.metadata = dict()
        label_frame = tk.LabelFrame(self, text="Metadata")
        label_frame.pack()
        tk.Label(label_frame, text="Key").grid(row=0)
        self.key_entry = tk.Entry(label_frame)
        self.key_entry.grid(row=0, column=1)
        tk.Label(label_frame, text="Value").grid(row=1)
        self.value_entry = tk.Entry(label_frame)
        self.value_entry.grid(row=1, column=1)
        tk.Button(label_frame, text="Add", command=self.add_metadata).grid(row=1, column=3)
        self.list_box = tk.Listbox(label_frame)
        self.list_box.grid(row=2, columnspan=3)

    def add_metadata(self):
        _key = self.key_entry.get()
        _value = self.value_entry.get()
        self.metadata[_key] = _value
        logger.info(f"Add metadata pair: {_key} {_value}")
        self.list_box.delete(0, tk.END)
        for key in sorted(self.metadata.keys()):
            value = self.metadata[key]
            self.list_box.insert(tk.END, f"{key}: {value}")
        logger.info(f"Current metadata: {self.metadata}")


class DataSetCreationWindow(tk.Toplevel):

    def __init__(self):
        super().__init__()
        self.title("Create new dataset")
        dataset_name_frame = DataSetNameFrame(self)
        data_directory_frame = DataDirectoryFrame(self)
        metadata_frame = MetaDataFrame(self)

        dataset_name_frame.pack()
        data_directory_frame.pack()
        metadata_frame.pack()


class ListDataSetsWindow(tk.Toplevel):

    def __init__(self):
        super().__init__()
        self.title("List datasets")

        self.base_uri = JUNK_DIR
        self.datasets = dict()
        self.dataset_list_box = tk.Listbox(self)
        self.dataset_list_box.pack()
        self.refresh_content()

    def refresh_content(self):
        self.dataset_list_box.delete(0, tk.END)
        for ds in iter_datasets_in_base_uri(self.base_uri):
            self.datasets[ds.name] = ds
            self.dataset_list_box.insert(tk.END, ds.name)
        logger.info(f"Loaded datasets: {self.datasets}")


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("dtool-gui")
        self.create_dataset_btn = tk.Button(
            self,
            text="Create new dataset",
            command=self.open_create_dataset_window
        )
        self.list_datasets_btn = tk.Button(
            self,
            text="List dataset",
            command=self.open_list_datasets_window
        )

        self.create_dataset_btn.pack()
        self.list_datasets_btn.pack()

    def open_create_dataset_window(self):
        DataSetCreationWindow().grab_set()

    def open_list_datasets_window(self):
        ListDataSetsWindow().grab_set()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
