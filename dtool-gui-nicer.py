import logging

import tkinter as tk

from dtoolcore.utils import name_is_valid

logger = logging.getLogger(__name__)


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


class DataSetCreationView(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("dtool dataset creator")
        dataset_name_frame = DataSetNameFrame(self)
        dataset_name_frame.pack()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = DataSetCreationView()
    app.mainloop()
