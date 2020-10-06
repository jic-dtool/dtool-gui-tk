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

    def load_master_schema(self, master_schema):
        "Load JSON schema of an object describing the metadata model."
        self._master_schema = master_schema
        for name, schema in self._master_schema["properties"].items():
            self._metadata_schema_items[name] = MetadataSchemaItem(schema)

    @property
    def required_item_names(self):
        "Return list of names of required metadata items."
        return self._master_schema["required"]

    @property
    def item_names(self):
        "Return metadata names (keys)."
        return sorted(self._master_schema["properties"].keys())

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
