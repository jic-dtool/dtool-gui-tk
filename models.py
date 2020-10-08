import dtoolcore.utils

from metadata import MetadataSchemaItem

LOCAL_BASE_URI_KEY = "DTOOL_LOCAL_BASE_URI"


class LocalBaseURIModel(object):
    "Model for managing local base URI."

    def __init__(self, config_path=None):
        self._config_path = config_path

    def get_base_uri(self):
        """Return the base URI."""
        return dtoolcore.utils.get_config_value_from_file(
            LOCAL_BASE_URI_KEY,
            self._config_path
        )

    def put_base_uri(self, base_uri):
        """Put/update the base URI in the config file."""
        dtoolcore.utils.write_config_value_to_file(
            LOCAL_BASE_URI_KEY,
            base_uri,
            self._config_path
        )


class MetadataModel(object):
    "Model for managing metadata."

    def __init__(self):
        self._metadata_schema_items = {}
        self._metadata_values = {}
        self._required_item_names = set()
        self._selected_optional_item_names = set()

    @property
    def item_names(self):
        "Return metadata names (keys)."
        return sorted(self._metadata_schema_items.keys())

    @property
    def required_item_names(self):
        "Return list of names of required metadata items."
        return sorted(list(self._required_item_names))

    @property
    def optional_item_names(self):
        "Return list of names of optional metadata items."
        all_set = set(self.item_names)
        required_set = set(self.required_item_names)
        return sorted(list(all_set - required_set))

    @property
    def selected_optional_item_names(self):
        "Return list of names of selected optional metadata items."
        return sorted(list(self._selected_optional_item_names))

    @property
    def deselected_optional_item_names(self):
        "Return list of names of deselected optional metadata items."
        optional_set = set(self.optional_item_names)
        selected_set = set(self.selected_optional_item_names)
        return sorted(list(optional_set - selected_set))

    def load_master_schema(self, master_schema):
        "Load JSON schema of an object describing the metadata model."
        for name, schema in master_schema["properties"].items():
            self._metadata_schema_items[name] = MetadataSchemaItem(schema)

        for r in master_schema["required"]:
            self._required_item_names.add(r)

    def add_metadata_property(self, name, schema={}, required=False):
        "Add a metadata property to the master schema."
        self._metadata_schema_items[name] = MetadataSchemaItem(schema)
        if required:
            self._required_item_names.add(name)

    def get_master_schema(self):
        "Return JSON schema of object describing the metadata model."
        master_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        for name in self.item_names:
            schema_item = self._metadata_schema_items[name]
            master_schema["properties"][name] = schema_item.schema
        for name in self.required_item_names:
            master_schema["required"].append(name)

        return master_schema

    def get_schema(self, name):
        "Return metadata schema."
        return self._metadata_schema_items[name]

    def get_value(self, name):
        "Return metadata value."
        if name not in self._metadata_values:
            return None
        return self._metadata_values[name]

    def set_value(self, name, value):
        "Set the metadata value."
        self._metadata_values[name] = value

    def is_okay(self, name):
        "Validate the metadata value against its schema."
        schema = self.get_schema(name)
        value = self.get_value(name)
        return schema.is_okay(value)

    def select_optional_item(self, name):
        "Mark an optinal metadata item as selected."
        if name in self.optional_item_names:
            self._selected_optional_item_names.add(name)

    def deselect_optional_item(self, name):
        "Mark an optinal metadata item as not selected."
        if name in self.selected_optional_item_names:
            self._selected_optional_item_names.remove(name)
