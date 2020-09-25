import os
import logging

import tkinter as tk
import tkinter.filedialog as fd

from dtoolcore.utils import name_is_valid

logger = logging.getLogger(__name__)

HOME_DIR = os.path.expanduser("~")


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
            return name_is_valid(name)
        return True

    def invalid_name(self):
        logging.info("Preventing invalid dataset name creation")


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
        logging.info(f"Data directory set to: {data_directory}")


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
        logging.info(f"Add metadata pair: {_key} {_value}")
        self.list_box.delete(0, tk.END)
        for key in sorted(self.metadata.keys()):
            value = self.metadata[key]
            self.list_box.insert(tk.END, f"{key}: {value}")
        logging.info(f"Current metadata: {self.metadata}")


class DataSetCreationView(tk.Toplevel):

    def __init__(self):
        super().__init__()
        self.title("dtool dataset creator")
        dataset_name_frame = DataSetNameFrame(self)
        data_directory_frame = DataDirectoryFrame(self)
        metadata_frame = MetaDataFrame(self)

        dataset_name_frame.pack()
        data_directory_frame.pack()
        metadata_frame.pack()


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.create_dataset_btn = tk.Button(
            self,
            text="Create new dataset",
            command=self.open_create_dataset_window
        )
        self.create_dataset_btn.pack()

    def open_create_dataset_window(self):
        dataset_creation_view = DataSetCreationView()
        dataset_creation_view.grab_set()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
