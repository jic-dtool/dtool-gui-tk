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


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        logger.info("Initialising GUI")
        self.title("MetadataModel spike GUI")
        self.metadata_model = MetadataModel()
        self.metadata_model.load_master_schema(MASTER_SCHEMA)

        self.labels = {}

        self._current_metadata_index = self.setup_required_metadata(0, 1)
        self.setup_optional_metadata_listbox(0, 0)

    def setup_optional_metadata_listbox(self, row, column):
        logger.info("Setting up optional metadata listbox")
        self.optional_metadata_listbox = tk.Listbox(self)
        self.optional_metadata_listbox.bind(
            "<<ListboxSelect>>",
            self.select_optional_metadata
        )
        rowspan = len(self.metadata_model.item_names)
        self.optional_metadata_listbox.grid(
            row=row,
            column=column,
            rowspan=rowspan
        )
        self.repopulate_optional_metadata_listbox()

    def repopulate_optional_metadata_listbox(self):
        self.optional_metadata_listbox.delete(0, tk.END)
        for name in self.metadata_model.deselected_optional_item_names:
            logger.info(f"Adding {name} to optional metadata listbox")
            self.optional_metadata_listbox.insert(tk.END, name)

    def setup_required_metadata(self, row, column):
        row_index = row
        for i, name in enumerate(self.metadata_model.required_item_names):
            lbl = tk.Label(self, text=name + "*")
            lbl.grid(row=row_index, column=column, sticky="e")
            self.labels[name] = lbl
            # self.setup_input_field(row, column, name)
            row_index = row_index + i
        return row_index + 1

    def select_optional_metadata(self, event):
        widget = event.widget
        index = int(widget.curselection()[0])
        name = widget.get(index)
        logger.info(f"Clicked optional metadata: {name}")
        self.metadata_model.select_optional_item(name)
        self.repopulate_optional_metadata_listbox()
        lbl = tk.Label(self, text=name)
        lbl.grid(row=self._current_metadata_index, column=1, sticky="e")
        self._current_metadata_index = self._current_metadata_index + 1
        self.labels[name] = lbl


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
