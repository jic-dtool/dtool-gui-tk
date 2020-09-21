import os
import logging

import tkinter as tk
import tkinter.filedialog as fd

import dtoolcore as dc
from dtoolcore.utils import (
    IS_WINDOWS,
    windows_to_unix_path,
)

logger = logging.getLogger(__name__)


HOME_DIR = os.path.expanduser("~")
CUR_DIR = os.getcwd()
JUNK_DIR = os.path.join(HOME_DIR, "junk")


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self._data_directory = CUR_DIR
        logging.info(f"Initilised data directory to: {self._data_directory}")

        dataset_name_lbl = tk.Label(text="Dataset name")
        self.dataset_name = tk.Entry(self)
        self.data_dir_btn = tk.Button(
            self,
            text="Select data directory",
            command=self.select_data_directory
        )
        freeze_btn = tk.Button(
            self,
            text="Create",
            command=self.create_dataset
        )

        dataset_name_lbl.pack(side=tk.LEFT)
        self.dataset_name.pack()
        self.data_dir_btn.pack()
        freeze_btn.pack()

    def select_data_directory(self):
        self._data_directory = fd.askdirectory(
            title="Select data directory",
            initialdir=HOME_DIR
        )
        logging.info(f"Data directory set to: {self._data_directory}")

    @property
    def data_directory(self):
        return self._data_directory

    @property
    def base_uri(self):
        return JUNK_DIR

    def _yield_path_handle_tuples(self):
        path_length = len(self.data_directory) + 1

        for dirpath, dirnames, filenames in os.walk(self.data_directory):
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                relative_path = path[path_length:]
                if IS_WINDOWS:
                    handle = windows_to_unix_path(relative_path)
                yield (path, handle)

    def create_dataset(self):
        dataset_name = self.dataset_name.get()
        logging.info(f"Creating {dataset_name} in {self.base_uri}")

        with dc.DataSetCreator(
            name=dataset_name,
            base_uri=self.base_uri
        ) as ds_creator:
            for fpath, handle in self._yield_path_handle_tuples():
                ds_creator.put_item(fpath, handle)
            dataset_uri = ds_creator.uri

        logging.info(f"Created dataset with URI: {dataset_uri}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
