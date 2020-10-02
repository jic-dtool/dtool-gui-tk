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


def yield_path_handle_tuples(data_directory):
    path_length = len(data_directory) + 1

    for dirpath, dirnames, filenames in os.walk(data_directory):
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            relative_path = path[path_length:]
            if dtoolcore.utils.IS_WINDOWS:
                handle = dtoolcore.utils.windows_to_unix_path(relative_path)
            yield (path, handle)


class DataSetNameFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        vcmd = (master.register(self.validate_callback), "%P")
        label_frame = tk.LabelFrame(self, text="Dataset name")
        label_frame.pack()
        self.entry = tk.Entry(
            label_frame,
            validate="key",
            validatecommand=vcmd,
            invalidcommand=self.invalid_name
        )
        self.entry.pack()

    @property
    def name(self):
        return self.entry.get()

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

    @property
    def data_directory(self):
        return self.entry.get()

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
        self._metadata = dict()
        label_frame = tk.LabelFrame(self, text="Metadata")
        label_frame.pack()
        tk.Label(label_frame, text="Key").grid(row=0)
        self.key_entry = tk.Entry(label_frame)
        self.key_entry.bind("<Return>", self.key_event)
        self.key_entry.grid(row=0, column=1)
        tk.Label(label_frame, text="Value").grid(row=1)
        self.value_entry = tk.Entry(label_frame)
        self.value_entry.bind("<Return>", self.value_event)
        self.value_entry.grid(row=1, column=1)
        self.btn = tk.Button(
            label_frame,
            text="Add",
            command=self.add_metadata
        )
        self.btn.bind("<Return>", self.value_event)
        self.btn.grid(row=1, column=3)
        self.list_box = tk.Listbox(label_frame)
        self.list_box.grid(row=2, columnspan=3)

    @property
    def metadata(self):
        return self._metadata

    def add_metadata(self):
        _key = self.key_entry.get()
        _value = self.value_entry.get()
        self._metadata[_key] = _value
        logger.info(f"Add metadata pair: {_key} {_value}")
        self.list_box.delete(0, tk.END)
        for key in sorted(self._metadata.keys()):
            value = self._metadata[key]
            self.list_box.insert(tk.END, f"{key}: {value}")
        logger.info(f"Current metadata: {self.metadata}")

    def key_event(self, event):
        self.value_entry.focus_set()

    def value_event(self, event):
        self.add_metadata()
        self.key_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)
        self.key_entry.focus_set()


class DataSetCreationWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Create new dataset")
        self.dataset_name_frame = DataSetNameFrame(self)
        self.data_directory_frame = DataDirectoryFrame(self)
        self.metadata_frame = MetaDataFrame(self)

        self.dataset_name_frame.pack()
        self.data_directory_frame.pack()
        self.metadata_frame.pack()

        self.base_uri = JUNK_DIR
        create_button = tk.Button(self, text="Create", command=self.create)
        create_button.pack()

    def create(self):
        dataset_name = self.dataset_name_frame.name
        data_directory = self.data_directory_frame.data_directory

        logger.info(f"Creating {dataset_name} in {self.base_uri} using files in {data_directory}")  # NOQA

        readme_lines = ["---"]
        with dtoolcore.DataSetCreator(
            name=dataset_name,
            base_uri=self.base_uri
        ) as ds_creator:
            for fpath, handle in yield_path_handle_tuples(data_directory):
                ds_creator.put_item(fpath, handle)
            for key, value in self.metadata_frame.metadata.items():
                ds_creator.put_annotation(key, value)
                readme_lines.append(f"{key}: {value}")
            ds_creator.put_readme("\n".join(readme_lines))
            dataset_uri = ds_creator.uri

        logger.info(f"Created dataset with URI: {dataset_uri}")


class ListDataSetsWindow(tk.Tk):

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
        self.dataset_creation_window = DataSetCreationWindow()
        self.dataset_creation_window.focus_set()
        self.dataset_creation_window.grab_set()

    def open_list_datasets_window(self):
        ListDataSetsWindow().grab_set()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
