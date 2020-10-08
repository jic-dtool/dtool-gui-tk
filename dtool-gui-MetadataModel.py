"""Spike to experiment with MetadataModel class."""

import logging
import tkinter as tk

from models import MetadataModel

logger = logging.getLogger(__file__)


MASTER_SCHEMA = {
    "type": "object",
    "properties": {
        "gears": {"type": "integer", "enum": [1, 3, 6, 18]},
        "age": {"type": "integer", "exclusiveMinimum": 0},
        "owner": {"type": "string"}
    },
    "required": ["owner"]
}


class OptionalMetadataFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.label_frame = tk.LabelFrame(self, text="Optional Metadata")
        self.label_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.setup_optional_metadata_listbox(0, 0)

    def setup_optional_metadata_listbox(self, row, column):
        logger.info("Setting up optional metadata listbox")
        self.optional_metadata_listbox = tk.Listbox(self.label_frame)
        self.optional_metadata_listbox.bind(
            "<<ListboxSelect>>",
            self.master.select_optional_metadata
        )
        rowspan = len(self.master.metadata_model.item_names)
        self.optional_metadata_listbox.grid(
            row=row,
            column=column,
            rowspan=rowspan
        )
        self.repopulate()

    def repopulate(self):
        self.optional_metadata_listbox.delete(0, tk.END)
        for name in self.master.metadata_model.deselected_optional_item_names:
            logger.info(f"Adding {name} to optional metadata listbox")
            self.optional_metadata_listbox.insert(tk.END, name)


class MetadataFormFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.labels = {}
        self.label_frame = tk.LabelFrame(self, text="MetadataForm")
        self.label_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.repopulate(0, 0)

    def repopulate(self, row, column):

        # Clear existing widgets.
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        initial_row = row
        row_index = row
        for i, name in enumerate(
                self.master.metadata_model.required_item_names \
                + self.master.metadata_model.selected_optional_item_names
        ):
            row_index = initial_row + i
            display_name = name
            if name in self.master.metadata_model.required_item_names:
                display_name = name + "*"
            lbl = tk.Label(self.label_frame, text=display_name)
            if name in self.master.metadata_model.optional_item_names:
                lbl.bind("<Button-1>", self.master.deselect_optional_metadata)
            lbl.grid(row=row_index, column=column, sticky="e")
            self.labels[name] = lbl
            # self.setup_input_field(row, column, name)

        return row_index + 1


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        logger.info("Initialising GUI")
        self.title("MetadataModel spike GUI")
        self.metadata_model = MetadataModel()
        self.metadata_model.load_master_schema(MASTER_SCHEMA)

        self.optional_metadata_frame = OptionalMetadataFrame(self)
        self.metadata_form_frame = MetadataFormFrame(self)

        self.optional_metadata_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.metadata_form_frame.pack(side=tk.LEFT, fill=tk.Y)


    def repopulate(self):
        self.optional_metadata_frame.repopulate()
        self.metadata_form_frame.repopulate(0, 0)

    def select_optional_metadata(self, event):
        widget = event.widget
        index = int(widget.curselection()[0])
        name = widget.get(index)
        logger.info(f"Selected optional metadata: {name}")
        self.metadata_model.select_optional_item(name)
        self.repopulate()

    def deselect_optional_metadata(self, event):
        widget = event.widget
        name = widget.cget("text")
        logger.info(f"Deselected optional metadata: {name}")
        self.metadata_model.deselect_optional_item(name)
        self.repopulate()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
