import os

import dtoolcore
import dtoolcore.utils

from metadata import MetadataSchemaItem

LOCAL_BASE_URI_KEY = "DTOOL_LOCAL_BASE_URI"


class DirectoryDoesNotExistError(IOError):
    pass


class MetadataValidationError(ValueError):
    pass


class MissingBaseURIModelError(ValueError):
    pass


class MissingDataSetNameError(ValueError):
    pass


class MissingInputDirectoryError(ValueError):
    pass


class MissingMetadataModelError(ValueError):
    pass


class MissingRequiredMetadataError(ValueError):
    pass


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
            dtoolcore.utils.sanitise_uri(base_uri),
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

    @property
    def in_scope_item_names(self):
        "Return required and selected optional item names."
        return self.required_item_names + self.selected_optional_item_names

    @property
    def issues(self):
        """Return list of issues with metadata.
        Only reports on issues that are required and optional metadata that has
        been selected.
        """
        _issues = []
        for item_name in self.in_scope_item_names:
            schema = self.get_schema(item_name)
            value = self.get_value(item_name)
            if value is not None:
                for i in schema.issues(value):
                    _issues.append((item_name, str(i)))
        return _issues

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


class ProtoDataSetModel(object):
    "Model for creating building up and creating a dataset."

    def __init__(self):
        self._name = None
        self._input_directory = None
        self._base_uri_model = None
        self._metadata_model = None
        self._uri = None

    @property
    def name(self):
        "Return the name to use for the dataset."
        return self._name

    @property
    def base_uri(self):
        "Return the base URI for the dataset."
        return self._base_uri_model.get_base_uri()

    @property
    def input_directory(self):
        "Return the path to the input directory."
        return self._input_directory

    @property
    def metadata_model(self):
        "Return the metadata model."
        return self._metadata_model

    @property
    def uri(self):
        "Return the URI of the created dataset."
        return self._uri

    def set_name(self, name):
        "Set the name to use for the dataset."
        self._name = name

    def set_input_directory(self, input_directory):
        """Set the input directory for the dataset creation process.

        :raises: dtool_gui.models.DirectoryDoesNotExistError if the input
                 directory does not exist
        """
        if not os.path.isdir(input_directory):
            raise(DirectoryDoesNotExistError(
                "Cannot set input directory to: {}".format(input_directory)
            ))
        self._input_directory = input_directory

    def set_base_uri_model(self, base_uri_model):
        """Set the base URI model.

        :params base_uri_model: dtool_gui.models.LocalBaseURIModel
        """
        self._base_uri_model = base_uri_model

    def set_metadata_model(self, metadata_model):
        """Set the metadata model.

        :params metadata_model: dtool_gui.models.MetadataModel
        """
        self._metadata_model = metadata_model

    def create(self):
        """Create the dataset in the base URI.

        :raises: dtool_gui.models.MissingInputDirectoryError if the input
                 directory has not been set>
                 dtool_gui.models.MissingDataSetNameError if the dataset
                 name has not been set.
                 dtool_gui.models.MissingBaseURIModelError if the base
                 URI model has not been set.
                 dtool_gui.models.MissingMetadataModelError if the metadata
                 model has not been set.
        """

        if self._name is None:
            raise(MissingDataSetNameError("Dataset name has not been set"))

        if self._input_directory is None:
            raise(MissingInputDirectoryError("Input directory has not been set"))

        if self._base_uri_model is None:
            raise(MissingBaseURIModelError("Base URI model has not been set"))

        if self._metadata_model is None:
            raise(MissingMetadataModelError("Metadata model has not been set"))

        for name in self.metadata_model.required_item_names:
            metadata = self.metadata_model.get_value(name)
            if metadata is None:
                raise(MissingRequiredMetadataError(
                    "Missing required metadata: {}".format(name)
                ))

        for name in self.metadata_model.in_scope_item_names:
            if not self.metadata_model.is_okay(name):
                value = self.metadata_model.get_value(name)
                raise(MetadataValidationError(
                    "Metadata {} value not valid: {}".format(name, value)
                ))

        with dtoolcore.DataSetCreator(self.name, self.base_uri) as ds_creator:
            self._uri = ds_creator.uri
