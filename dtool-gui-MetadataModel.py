"""Spike to experiment with MetadataModel class."""

import logging
import tkinter as tk
import tkinter.ttk as ttk

from models import MetadataModel

logger = logging.getLogger(__file__)


MASTER_SCHEMA = {
    "type": "object",
    "properties": {
        "gears": {"type": "integer", "enum": [1, 3, 6, 18]},
        "age": {"type": "integer", "exclusiveMinimum": 0},
        "owner": {"type": "string", "minLength": 4},
        "project": {"type": "string", "minLength": 4},
        "pooled": {"type": "boolean"}
    },
    "required": ["project", "owner", "pooled"]
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
        schema = self.master.metadata_model.get_schema(name)
        value = string_to_typed(value_as_str, schema.type)
        logger.info(f"Set {widget.name} to {value}")
        self.master.metadata_model.set_value(name, value)
        self.update()
        self.master.issues_frame.update()

    def value_update_event_focus_in(self, event):
        widget = event.widget
        name = widget.name
        self._value_update_event(event)
        self.entries[name].focus_set()

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

    def setup_input_field(self, row, name):
        schema = self.master.metadata_model.get_schema(name)

        display_name = name
        if name in self.master.metadata_model.required_item_names:
            display_name = name + "*"

        lbl = tk.Label(self.label_frame, text=display_name)
        lbl.grid(row=row, column=0, sticky="e")

        value = self.master.metadata_model.get_value(name)
        logger.info(f"Setup input field {name} current value {value}")

        if schema.type == "boolean":
            values = ["True", "False"]
            e = ttk.Combobox(self.label_frame, state="readonly", values=values)
            index = None
            if value is not None:
                index = values.index(str(value))
            if index is not None:
                e.current(index)
            e.name = name
            e.bind("<<ComboboxSelected>>", self.value_update_event_focus_next)
            e.bind("<Return>", self.value_update_event_focus_next)
            e.grid(row=row, column=1, sticky="ew")
            self.entries[name] = e
        elif schema.enum is None:
            e = tk.Entry(self.label_frame)
            if value is not None:
                e.insert(0, str(value))
            e.name = name
            e.bind("<Button-1>", self.value_update_event_focus_in)
            e.bind("<Return>", self.value_update_event_focus_next)
            e.bind("<Tab>", self.value_update_event_focus_next)
            e.grid(row=row, column=1, sticky="ew")
            self.entries[name] = e
        else:
            values = [str(v) for v in schema.enum]
            e = ttk.Combobox(self.label_frame, state="readonly", values=values)
            index = None
            if value is not None:
                index = values.index(str(value))
            if index is not None:
                e.current(index)
            e.name = name
            e.bind("<<ComboboxSelected>>", self.value_update_event_focus_next)
            e.grid(row=row, column=1, sticky="ew")
            self.entries[name] = e

        if name in self.master.metadata_model.optional_item_names:
            btn = tk.Button(self.label_frame, text="Remove")
            btn._name_to_clear = name
            btn.bind("<Button-1>", self.master.deselect_optional_metadata)
            btn.grid(row=row, column=2)

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
        self.metadata_model = MetadataModel()
        self.metadata_model.load_master_schema(MASTER_SCHEMA)

        self.optional_metadata_frame = OptionalMetadataFrame(self)
        self.metadata_form_frame = MetadataFormFrame(self)
        self.issues_frame = IssuesFrame(self)

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()
