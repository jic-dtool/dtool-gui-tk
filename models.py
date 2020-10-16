import os
import logging
import json

import dtoolcore
import dtoolcore.utils

from metadata import MetadataSchemaItem

logger = logging.getLogger(__name__)

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


class UnsupportedTypeError(TypeError):
    pass


class _ConfigFileVariableBaseModel(object):

    def __init__(self, config_path=None):
        self._config_path = config_path

    def _get(self):
        """Return the base URI."""
        return dtoolcore.utils.get_config_value_from_file(
            self.KEY,
            self._config_path
        )

    def _put(self, value):
        """Put/update the base URI in the config file."""
        dtoolcore.utils.write_config_value_to_file(
            self.KEY,
            value,
            self._config_path
        )


class LocalBaseURIModel(_ConfigFileVariableBaseModel):
    "Model for managing local base URI."

    KEY = "DTOOL_LOCAL_BASE_URI"

    def get_base_uri(self):
        """Return the base URI."""
        return self._get()

    def put_base_uri(self, base_uri):
        """Put/update the base URI in the config file."""
        value = dtoolcore.utils.sanitise_uri(base_uri)
        self._put(value)


class MetadataSchemaListModel(_ConfigFileVariableBaseModel):
    "Model for managing list of metadata schama."

    KEY = "DTOOL_METADATA_SCHEMA_DIRECTORY"

    def get_metadata_schema_directory(self):
        """Return the metadata schema directory."""
        return self._get()

    def put_metadata_schema_directory(self, metadata_schema_directory):
        """Put/update the base URI in the config file."""
        value = os.path.abspath(metadata_schema_directory)
        self._put(value)

    @property
    def metadata_model_names(self):
        """Return list of metadata model names."""
        metadata_schema_directory = self.get_metadata_schema_directory()
        if metadata_schema_directory is None:
            return []
        filenames = os.listdir(metadata_schema_directory)
        return sorted([os.path.splitext(f)[0] for f in filenames])

    def get_metadata_model(self, name):
        """Returns class:`dtool_gui.models.MetadataModel` instance."""
        metadata_schema_directory = self.get_metadata_schema_directory()
        schema_fpath = os.path.join(metadata_schema_directory, name + ".json")
        metadata_model = MetadataModel()
        with open(schema_fpath) as fh:
            master_schema = json.load(fh)
        metadata_model.load_master_schema(master_schema)
        return metadata_model


class MetadataModel(object):
    "Model for managing metadata."

    def __init__(self):
        self._metadata_schema_items = {}
        self._metadata_values = {}
        self._required_item_names = set()
        self._selected_optional_item_names = set()

    def __eq__(self, other):
        if not self._metadata_schema_items == other._metadata_schema_items:
            return False
        if not self._metadata_values == other._metadata_values:
            return False
        if not self._required_item_names == other._required_item_names:
            return False
        if not self._selected_optional_item_names == other._selected_optional_item_names:  # NOQA
            return False
        return True

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

        if "required" in master_schema:
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

    def set_value_from_str(self, name, value_as_str):
        "Set the metadata value from a string forcing the type."
        type_ = self.get_schema(name).type
        if type_ == "string":
            if value_as_str == "":
                self.set_value(name, None)
            else:
                self.set_value(name, value_as_str)
        elif type_ == "integer":
            try:
                logger.info("Forcing type to integer")
                self.set_value(name, int(value_as_str))
            except ValueError:
                logger.warning("Could not force to integer")
                self.set_value(name, None)
        elif type_ == "number":
            try:
                logger.info("Forcing type to float")
                self.set_value(name, float(value_as_str))
            except ValueError:
                logger.warning("Could not force to float")
                self.set_value(name, None)
        elif type_ == "boolean":
            logger.info("Forcing type to bool")
            if value_as_str == "True":
                self.set_value(name, True)
            elif value_as_str == "False":
                self.set_value(name, False)
            else:
                logger.warning("Could not force to bool")
                self.set_value(name, None)
        else:
            raise(UnsupportedTypeError("{} not supported yet".format(type_)))

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

    def _yield_path_handle_tuples(self):
        path_length = len(self.input_directory) + 1

        for dirpath, dirnames, filenames in os.walk(self.input_directory):
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                relative_path = path[path_length:]
                if dtoolcore.utils.IS_WINDOWS:
                    handle = dtoolcore.utils.windows_to_unix_path(relative_path)  # NOQA
                yield (path, handle)

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
            raise(MissingInputDirectoryError("Input directory has not been set"))  # NOQA

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

            # Add metadata.
            readme_lines = ["---"]
            for key in self.metadata_model.in_scope_item_names:
                value = self.metadata_model.get_value(key)
                ds_creator.put_annotation(key, value)
                readme_lines.append("{}: {}".format(key, value))
            ds_creator.put_readme("\n".join(readme_lines))

            # Add data items.
            for fpath, handle in self._yield_path_handle_tuples():
                ds_creator.put_item(fpath, handle)

            self._uri = ds_creator.uri


class DataSetListModel(object):
    "Model for managing dataset in a base URI."

    def __init__(self):
        self._base_uri_model = None
        self._datasets = []

    @property
    def base_uri(self):
        "Return base URI."
        if self._base_uri_model is None:
            return None
        return self._base_uri_model.get_base_uri()

    @property
    def names(self):
        "Return list of dataset names."
        return [ds.name for ds in self._datasets]

    def set_base_uri_model(self, base_uri_model):
        """Set the base URI model.

        :params base_uri_model: dtool_gui.models.LocalBaseURIModel
        """
        self._base_uri_model = base_uri_model

    def get_uri(self, index):
        """Return the URI of the dataset at a specific index in the list.

        :param index: position of dataset in list
        """
        return self._datasets[index].uri

    def reindex(self):
        """Index the base URI."""
        self._datasets = []
        base_uri = self._base_uri_model.get_base_uri()
        for ds in dtoolcore.iter_datasets_in_base_uri(base_uri):
            self._datasets.append(ds)
