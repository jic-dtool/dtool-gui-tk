"""Spike GUI code to experiment with metadata validation."""

import logging
import tkinter as tk
import tkinter.ttk as ttk

from metadata import MetadataSchemaItem

logger = logging.getLogger(__file__)


PROJECT_SCHEMA = {"type": "string", "minLength": 3, "maxLength": 80}
NUCLEIC_ACID_SCHEMA = {"type": "string", "enum": ["DNA", "RNA"]}
AGE_SCHEMA = {"type": "integer", "minimum": 18, "maximum": 65}
TEMPERATURE_SCHEMA = {"type": "number", "exclusiveMaximum": 0}
POOLED_SCHEMA = {"type": "boolean"}
SPECIES = {
    "type": "string",
    "enum": [
        "A. australe",
        "A. barrelieri",
        "A. boissieri",
        "A. charidemi",
        "A. cirrhigerum",
        "A. graniticum",
        "A. hispanicum",
        "A. latifolium",
        "A. linkianum",
        "A. litigiosum",
        "A. majus",
        "A. mollissimum",
        "A. pseudomajus",
        "A. rupestre",
        "A. siculum",
        "A. striatum",
        "A. tortuosum",
        "A. lopesianum",
        "A. microphyllum",
        "A. molle",
        "A. pertegasii",
        "A. pulverulentum",
        "A. sempervirens",
        "A. subbaeticum",
        "A. valentinum",
        "A. braun-blanquetii",
        "A. grosii",
        "A. meonanthum",
    ]
}

class UnsupportedTypeError(TypeError):
    pass


def string_to_typed(str_, type_):
    if type_ == "string":
        if str_ == "":
            return None
        return str_
    elif type_ == "integer":
        try:
            logger.info("Forcing type to integer")
            return int(str_)
        except ValueError:
            logger.warning("Could not force to integer")
            return None
    elif type_ == "number":
        try:
            logger.info("Forcing type to float")
            return float(str_)
        except ValueError:
            logger.warning("Could not force to float")
            return None
    elif type_ == "boolean":
        logger.info("Forcing type to bool")
        if str_ == "True":
            return True
        elif str_ == "False":
            return False
        else:
            logger.warning("Could not force to bool")
            return None
    else:
        raise(UnsupportedTypeError(f"{type_} not supported yet"))


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        logger.info("Initialising GUI")
        self.title("Metadata spike GUI")
        self.labels = {}
        self.issues = {}
        self.metadata_entries = {}
        self.metadata_schemas = {
            "project": MetadataSchemaItem(PROJECT_SCHEMA),
            "nucl_acid": MetadataSchemaItem(NUCLEIC_ACID_SCHEMA),
            "age": MetadataSchemaItem(AGE_SCHEMA),
            "temperature": MetadataSchemaItem(TEMPERATURE_SCHEMA),
            "pooled": MetadataSchemaItem(POOLED_SCHEMA),
            "species": MetadataSchemaItem(SPECIES),
        }

        row = self.setup_issues_listbox(0)
        row = self.setup_metadata(row)


        self.create_button = tk.Button(
            self,
            text="Create",
            command=self.create,
            state="disabled"
        )
        self.create_button.grid(row=row, column=0, columnspan=2, sticky="ew")

        self.report_issues()

    def setup_issues_listbox(self, initial_row):
        self.issues_listbox = tk.Listbox(self, height=3)
        self.issues_listbox.grid(
            row=initial_row,
            column=0,
            columnspan=2,
            sticky="ew"
        )
        return initial_row + 1

    def get_metadata(self, key):
        value_str = self.metadata_entries[key].get()
        value_type = self.metadata_schemas[key].type
        value = string_to_typed(value_str, value_type)  # Need a transform to go to non-string types.
        logger.info(f"Getting metadata for {key}: {value}")
        return value

    def validate_metadata(self, key):
        value = self.get_metadata(key)
        okay = self.metadata_schemas[key].is_okay(value)
        logger.info(f"{key}={value} okay={okay}")
        if not okay:
            self.issues[key] = self.metadata_schemas[key].issues(value)
            self.metadata_entries[key].config({"background": "pink"})
        else:
            if key in self.issues:
                del self.issues[key]
            self.metadata_entries[key].config({"background": "white"})
        self.report_issues()
        return okay

    def setup_input_field(self, row, key):

        schema = self.metadata_schemas[key]
        if schema.type == "boolean":
            e = ttk.Combobox(self, state="readonly", values=["True", "False"])
            e.grid(row=row, column=1, sticky="ew")
            self.metadata_entries[key] = e
        elif schema.enum is None:
            vcmd = (self.register(self.validate_metadata), key)
            e = tk.Entry(self, validate="focusout", validatecommand=vcmd)
            e.grid(row=row, column=1, sticky="ew")
            self.metadata_entries[key] = e
        else:
            e = ttk.Combobox(self, state="readonly", values=schema.enum)
            e.grid(row=row, column=1, sticky="ew")
            self.metadata_entries[key] = e

    def setup_metadata(self, initial_row):
        _row = initial_row
        for row, key in enumerate(sorted(self.metadata_schemas.keys())):

            current_row = row + initial_row
            lbl = tk.Label(text=key)
            lbl.grid(row=current_row, column=0, sticky="e")
            self.labels[key] = lbl

            self.setup_input_field(current_row, key)
            _row = current_row
        return _row + 1


    def report_issues(self):
        any_issue = False
        self.issues_listbox.delete(0, tk.END)
        if None in [self.get_metadata(k) for k in self.metadata_schemas.keys()]:
            self.issues_listbox.insert(tk.END, "All fields need to be completed")
            any_issue = True
        for key in sorted(self.issues.keys()):
            for issue in self.issues[key]:
                any_issue = True
                self.issues_listbox.insert(tk.END, f"{key}: {issue}")
        if not any_issue:
            self.create_button.config({"state": "active"})

    def create(self):
        for key in sorted(self.metadata_schemas.keys()):
            print(key)
            value = self.get_metadata(key)
            logger.info(f"Creating {key}: {value} pair")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
