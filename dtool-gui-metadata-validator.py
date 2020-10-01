"""Spike GUI code to experiment with metadata validation."""

import logging
import tkinter as tk
import tkinter.ttk as ttk

from metadata import MetadataSchemaItem

logger = logging.getLogger(__file__)


PROJECT_SCHEMA = {"type": "string", "minLength": 3, "maxLength": 80}
NUCLEIC_ACID_SCHEMA = {"type": "string", "enum": ["DNA", "RNA"]}
AGE_SCHEMA = {"type": "integer", "minimum": 18, "maximum": 65}

class UnsupportedTypeError(TypeError):
    pass


def string_to_typed(str_, type_):
    if type_ == "string":
        return str_
    elif type_ == "integer":
        logger.info("Forcing type to integer")
        return int(str_)
    elif type_ == "float":
        logger.info("Forcing type to float")
        return float(str_)
    else:
        raise(UnsupportedTypeError(f"{type_} not supported yet"))


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        logger.info("Initialising GUI")
        self.title("Metadata spike GUI")
        self.labels = {}
        self.metadata_entries = {}
        self.metadata_schemas = {
            "project": MetadataSchemaItem(PROJECT_SCHEMA),
            "nucl_acid": MetadataSchemaItem(NUCLEIC_ACID_SCHEMA),
            "age": MetadataSchemaItem(AGE_SCHEMA),
        }
        self.setup_metadata()

    def get_metadata(self, key):
        value_str = self.metadata_entries[key].get()
        value_type = self.metadata_schemas[key].type
        value = string_to_typed(value_str, value_type)  # Need a transform to go to non-string types.
        logger.info("Getting metadata for {key}: {value}")
        return value

    def validate_metadata(self, key):
        value = self.get_metadata(key)
        okay = self.metadata_schemas[key].is_okay(value)
        logger.info(f"{key}={value} okay={okay}")
        if not okay:
            issues = "\n".join(self.metadata_schemas[key].issues(value))
            self.metadata_entries[key].config({"background": "pink"})
            self.labels[key].config({"text": f"{key} ({issues})"})
        else:
            self.metadata_entries[key].config({"background": "white"})
            self.labels[key].config({"text": f"{key}"})
        return okay

    def setup_input_field(self, row, key):

            schema = self.metadata_schemas[key]
            if schema.enum is None:
                vcmd = (self.register(self.validate_metadata), key)
                e = tk.Entry(self, validate="focusout", validatecommand=vcmd)
                e.grid(row=row, column=1)
                self.metadata_entries[key] = e
            else:
                e = ttk.Combobox(self, values=schema.enum)
                e.grid(row=row, column=1)
                self.metadata_entries[key] = e

    def setup_metadata(self):
        for row, key in enumerate(sorted(self.metadata_schemas.keys())):

            lbl = tk.Label(text=key)
            lbl.grid(row=row, column=0)
            self.labels[key] = lbl

            self.setup_input_field(row, key)

#           vcmd = (self.register(self.validate_metadata), key)
#           e = tk.Entry(self, validate="focusout", validatecommand=vcmd)
#           e.grid(row=row, column=1)
#           self.metadata_entries[key] = e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
