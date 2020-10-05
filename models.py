import dtoolcore.utils

LOCAL_BASE_URI_KEY="DTOOL_LOCAL_BASE_URI"


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

    def load_master_schema(self, master_schema):
        self._master_schema = master_schema

    @property
    def required_item_names(self):
        return self._master_schema["required"]

    @property
    def item_names(self):
        return sorted(self._master_schema["properties"].keys())
