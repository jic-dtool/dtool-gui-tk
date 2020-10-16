"""Spike to experiment with MetadataModel class."""

import os
import logging
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk

import dtoolcore.utils

from models import LocalBaseURIModel, MetadataModel, ProtoDataSetModel

logger = logging.getLogger(__file__)

HOME_DIR = os.path.expanduser("~")

MASTER_SCHEMA = {
    "type": "object",
    "properties": {
        "project": {"type": "string", "minLength": 3, "maxLength": 80},
        "nucl_acid": {"type": "string", "enum": ["DNA", "RNA"]},
        "age": {"type": "integer", "exclusiveMinimum": 0},
        "temperature": {"type": "number", "enum": [4.0, 25.0]},
        "pooled": {"type": "boolean"},
        "species": {
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
    },
    "required": ["project", "nucl_acid", "pooled", "species"]
}


def set_combobox_default_selection(combobox, choices, selected):
    index = None
    if selected is not None:
        index = choices.index(str(selected))
    if index is not None:
        combobox.current(index)


class DataSetFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.label_frame = tk.LabelFrame(self, text="Dataset Info")
        self.label_frame.pack()
        self.entries = {}

        self.update()

    def validate_name_callback(self, name):
        if (name is not None) and (len(name) > 0):
            return dtoolcore.utils.name_is_valid(name)
        return True

    def update_name(self, event):
        widget = event.widget
        name = widget.get()
        if (name is not None) and name != "":
            logger.info(f"Setting dataset name to: {name}")
            self.master.proto_dataset_model.set_name(name)
        self.update()

    def select_data_directory(self):
        data_directory = fd.askdirectory(
            title="Select data directory",
            initialdir=HOME_DIR
        )
        self.master.proto_dataset_model.set_input_directory(data_directory)
        logger.info(f"Data directory set to: {data_directory}")
        self.update()

    def select_local_base_uri_directory(self):
        base_uri_directory = fd.askdirectory(
            title="Select data directory",
            initialdir=HOME_DIR
        )
        self.master.base_uri_model.put_base_uri(base_uri_directory)
        logger.info(f"Local base URI directory set to: {base_uri_directory}")
        self.update()

    def setup_name_input_field(self, row):

        vcmd = (self.master.register(self.validate_name_callback), "%P")
        lbl = tk.Label(self.label_frame, text="Dataset Name")
        entry = tk.Entry(
            self.label_frame,
            validate="key",
            validatecommand=vcmd,
        )

        current_name = self.master.proto_dataset_model.name
        if current_name is not None:
            entry.insert(0, current_name)

        entry.bind("<FocusOut>", self.update_name)
        entry.bind("<Return>", self.update_name)
        entry.bind("<Tab>", self.update_name)

        lbl.grid(row=row, column=0)
        entry.grid(row=row, column=1)

    def setup_input_directory_field(self, row):
        lbl = tk.Label(self.label_frame, text="Input data directory")
        logger.info(f"Current input directory: {self.master.proto_dataset_model.input_directory}")
        entry = tk.Entry(
            self.label_frame,
            )
        current_input_dir = self.master.proto_dataset_model.input_directory
        if current_input_dir is not None:
            entry.insert(0, current_input_dir)
        entry.configure(state="readonly")

        btn = tk.Button(
            self.label_frame,
            text="Select data directory",
            command=self.select_data_directory
        )
        lbl.grid(row=row, column=0)
        entry.grid(row=row, column=1)
        btn.grid(row=row, column=2)

    def setup_local_base_uri_directory(self, row):
        lbl = tk.Label(self.label_frame, text="Local base URI directory")
        current_local_base_uri = self.master.base_uri_model.get_base_uri()
        logger.info(f"Current local base URI directory: {current_local_base_uri}")
        entry = tk.Entry(
            self.label_frame,
            )
        if current_local_base_uri is not None:
            entry.insert(0, current_local_base_uri)
        entry.configure(state="readonly")

        btn = tk.Button(
            self.label_frame,
            text="Select local base URI directory",
            command=self.select_local_base_uri_directory
        )
        lbl.grid(row=row, column=0)
        entry.grid(row=row, column=1)
        btn.grid(row=row, column=2)


    def update(self):

        for widget in self.label_frame.winfo_children():
            widget.destroy()

        self.setup_name_input_field(0)
        self.setup_input_directory_field(1)
        self.setup_local_base_uri_directory(2)


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
        self.update()

    def update(self):
        self.optional_metadata_listbox.delete(0, tk.END)
        for name in self.master.metadata_model.deselected_optional_item_names:
            logger.info(f"Adding {name} to optional metadata listbox")
            self.optional_metadata_listbox.insert(tk.END, name)


class MetadataFormFrame(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.labels = {}
        self.entries = {}
        self.label_frame = tk.LabelFrame(self, text="MetadataForm")
        self.label_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.update()

    def _value_update_event(self, event):
        widget = event.widget
        name = widget.name
        value_as_str = widget.get()
        if (value_as_str is not None) and (value_as_str != ""):
            logger.info(f"Setting {name} to: {value_as_str}")
            self.master.metadata_model.set_value_from_str(name, value_as_str)
        self.update()
        self.master.issues_frame.update()

    def value_update_event_focus_out(self, event):
        widget = event.widget
        name = widget.name
        self._value_update_event(event)

    def value_update_event_focus_next(self, event):
        widget = event.widget
        name = widget.name
        self._value_update_event(event)
        index = self.master.metadata_model.in_scope_item_names.index(name)
        next_index = index + 1
        if next_index >= len(self.master.metadata_model.in_scope_item_names):
            next_index = 0
        next_name = self.master.metadata_model.in_scope_item_names[next_index]
        self.entries[next_name].focus_set()

    def setup_boolean_input_field(self, row, name, value):
        values = ["True", "False"]
        e = ttk.Combobox(self.label_frame, state="readonly", values=values)
        set_combobox_default_selection(e, values, value)
        e.name = name
        e.bind("<<ComboboxSelected>>", self.value_update_event_focus_next)
        e.bind("<Return>", self.value_update_event_focus_next)
        e.grid(row=row, column=1, sticky="ew")
        self.entries[name] = e

    def setup_entry_input_field(self, row, name, value):
        e = tk.Entry(self.label_frame)
        if value is not None:
            e.insert(0, str(value))
        e.name = name
        e.bind("<FocusOut>", self.value_update_event_focus_out)
        e.bind("<Return>", self.value_update_event_focus_next)
        e.bind("<Tab>", self.value_update_event_focus_next)
        e.grid(row=row, column=1, sticky="ew")
        self.entries[name] = e

    def setup_enum_input_field(self, row, name, value):
        schema = self.master.metadata_model.get_schema(name)
        values = [str(v) for v in schema.enum]
        e = ttk.Combobox(self.label_frame, state="readonly", values=values)
        set_combobox_default_selection(e, values, value)
        e.name = name
        e.bind("<<ComboboxSelected>>", self.value_update_event_focus_next)
        e.grid(row=row, column=1, sticky="ew")
        self.entries[name] = e

    def setup_input_field(self, row, name):
        schema = self.master.metadata_model.get_schema(name)

        # Create the label.
        display_name = name
        if name in self.master.metadata_model.required_item_names:
            display_name = name + "*"

        lbl = tk.Label(self.label_frame, text=display_name)
        lbl.grid(row=row, column=0, sticky="e")

        value = self.master.metadata_model.get_value(name)

        # Create the input field.
        if schema.type == "boolean":
            self.setup_boolean_input_field(row, name, value)
        elif schema.enum is None:
            self.setup_entry_input_field(row, name, value)
        else:
            self.setup_enum_input_field(row, name, value)

        # Add button to enable the removal of the field if it is optional.
        if name in self.master.metadata_model.optional_item_names:
            btn = tk.Button(self.label_frame, text="Remove")
            btn._name_to_clear = name
            btn.bind("<Button-1>", self.master.deselect_optional_metadata)
            btn.grid(row=row, column=2)

        # Highlight input field if the value is invalid.
        background = "white"
        if value is not None and not self.master.metadata_model.is_okay(name):
            background = "pink"
        self.entries[name].config({"background": background})

    def update(self):

        # Clear existing widgets.
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        self.entries = {}

        for i, name in enumerate(
                self.master.metadata_model.required_item_names
                + self.master.metadata_model.selected_optional_item_names
        ):
            self.setup_input_field(i, name)


class IssuesFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.label_frame = tk.LabelFrame(self, text="Validation issues")
        self.issues_listbox = tk.Listbox(self.label_frame)
        self.label_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.issues_listbox.pack(fill=tk.Y)

    def update(self):
        self.issues_listbox.delete(0, tk.END)
        for name, issue in self.master.metadata_model.issues:
            self.issues_listbox.insert(tk.END, f"{name}: {issue}")


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        logger.info("Initialising GUI")
        self.title("MetadataModel spike GUI")

        self.base_uri_model = LocalBaseURIModel()

        self.metadata_model = MetadataModel()
        self.metadata_model.load_master_schema(MASTER_SCHEMA)

        self.proto_dataset_model = ProtoDataSetModel()
        self.proto_dataset_model.set_base_uri_model(self.base_uri_model)
        self.proto_dataset_model.set_metadata_model(self.metadata_model)

        self.optional_metadata_frame = OptionalMetadataFrame(self)
        self.metadata_form_frame = MetadataFormFrame(self)
        self.issues_frame = IssuesFrame(self)

        self.dataset_frame = DataSetFrame(self)
        self.dataset_frame.pack(side=tk.TOP, fill=tk.X)

        label_frame = tk.LabelFrame(self, text="More stuff").pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(label_frame, text="Create", command=self.create).pack(side=tk.BOTTOM)

        self.optional_metadata_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.metadata_form_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.issues_frame.pack(side=tk.LEFT, fill=tk.Y)


    def update(self):
        self.optional_metadata_frame.update()
        self.metadata_form_frame.update()
        self.issues_frame.update()

    def select_optional_metadata(self, event):
        widget = event.widget
        try:
            index = int(widget.curselection()[0])
        except IndexError:
            return
        name = widget.get(index)
        logger.info(f"Selected optional metadata: {name}")
        self.metadata_model.select_optional_item(name)
        self.update()
        self.metadata_form_frame.entries[name].focus_set()

    def deselect_optional_metadata(self, event):
        widget = event.widget
        name = widget._name_to_clear
        logger.info(f"Deselected optional metadata: {name}")
        self.metadata_model.deselect_optional_item(name)
        self.update()

    def create(self):
        self.proto_dataset_model.create()
        logger.info(f"Created dataset: {self.proto_dataset_model.uri}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
