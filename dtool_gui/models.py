import os
import logging
import json

import dtoolcore
import dtoolcore.utils

from ruamel.yaml import YAML

# This is a hack.
from dtool_info.inventory import _dataset_info

from dtool_gui.metadata import MetadataSchemaItem

logger = logging.getLogger(__name__)

LOCAL_BASE_URI_KEY = "DTOOL_LOCAL_BASE_URI"
METADATA_SCHEMA_ANNOTATION_NAME = "_metadata_schema"


def get_json_schema_type(obj):
    """Return JSON schema type representation of object.

    :param obj: object to return the JSON schema type for
    :returns: JSON schema type as a string
    :raises: :class:`dtool_gui.models.UnsupportedTypeError` if the value is a
             complex data structure. Currently supported data types are
             ``str``, ``int``, ``float``, and ``bool``.
    """
    if isinstance(obj, str):
        return "string"
    # This check needs to be before int because bool is subclass of int.
    elif isinstance(obj, bool):
        return "boolean"
    elif isinstance(obj, int):
        return "integer"
    elif isinstance(obj, float):
        return "number"
    else:
        raise(UnsupportedTypeError("{} not supported yet".format(type(obj))))


def metadata_model_from_dataset(dataset):
    """Return MetadataModel from a dataset.

    Schema extracted from the readme and annotations. Specifically,
    if an annotation named "_metadata_schema" it is loaded. Key value pairs
    from the readme are then added. Key value pairs are then extracted from
    the dataset annotations (the "_metdata_schema" key is ignored).

    The precedent for determining the type for a schema item is to use the
    type defined in the "_metadata_schema" if present, if not the type of
    the value extracted from the dataset is used.

    :param dataset: :class:`dtoolcore.DataSet`
    :returns: :class:`dtool_gui.models.MetadataModel` instance
    :raises dtool_gui.models.MetadataConflictError: if the values extracted
        from the readme and annotations do not match for a particular key
    :raises dtool_gui.models.UnsupportedTypeError: if the value is not
        supported, see :func:`dtool_gui.models.get_json_schema_type`.
    """
    metadata_model = MetadataModel()

    ignore_metadata_schemas = set()
    if METADATA_SCHEMA_ANNOTATION_NAME in dataset.list_annotation_names():
        schema = dataset.get_annotation(METADATA_SCHEMA_ANNOTATION_NAME)
        metadata_model.load_master_schema(schema)
        for name in metadata_model.item_names:
            ignore_metadata_schemas.add(name)

    yaml = YAML()
    readme_dict = yaml.load(dataset.get_readme_content())
    if readme_dict is None:
        readme_dict = {}

    if isinstance(readme_dict, dict):
        for key in readme_dict.keys():
            value = readme_dict[key]
            _type = get_json_schema_type(value)
            schema = {"type": _type}

            # Only add schema items not added from "_metadata_schema".
            if key not in ignore_metadata_schemas:
                metadata_model.add_metadata_property(key, schema, True)

            # Update the value regardless.
            metadata_model.set_value(key, value)

    for key in dataset.list_annotation_names():

        # Ignore the special key that stores a schema.
        if key == METADATA_SCHEMA_ANNOTATION_NAME:
            continue

        value = dataset.get_annotation(key)
        _type = get_json_schema_type(value)
        schema = {"type": _type}

        if key in readme_dict:
            readme_value = readme_dict[key]
            if readme_value != value:
                err_msg = "Annotation ({}) and readme ({}) values do not match for key {}"  # NOQA
                raise(MetadataConflictError(
                    err_msg.format(readme_value, value, key)
                    )
                )

        # Only add schema items not added from "_metadata_schema".
        if key not in ignore_metadata_schemas:
            metadata_model.add_metadata_property(key, schema, True)

        # Update the value regardless.
        metadata_model.set_value(key, dataset.get_annotation(key))

    return metadata_model


class DirectoryDoesNotExistError(IOError):
    pass


class MetadataValidationError(ValueError):
    pass


class MetadataConflictError(ValueError):
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
        return dtoolcore.utils.get_config_value_from_file(
            self.KEY,
            self._config_path
        )

    def _put(self, value):
        dtoolcore.utils.write_config_value_to_file(
            self.KEY,
            value,
            self._config_path
        )


class LocalBaseURIModel(_ConfigFileVariableBaseModel):
    "Model for managing local base URI."

    KEY = "DTOOL_LOCAL_BASE_URI"

    def get_base_uri(self):
        """Return the base URI.

        :returns: base URI where datasets will be read from and written to
        """
        return self._get()

    def put_base_uri(self, base_uri):
        """Put/update the base URI.

        The value is updated in the config file.

        :param base_uri: base URI
        """
        value = dtoolcore.utils.sanitise_uri(base_uri)
        self._put(value)


class MetadataSchemaListModel(_ConfigFileVariableBaseModel):
    "Model for managing list of metadata schama."

    KEY = "DTOOL_METADATA_SCHEMA_DIRECTORY"

    def get_metadata_schema_directory(self):
        """Return the metadata schema directory.

        :returns: absolute path to directory where metadata schemas are stored
                  as JSON files
        """
        return self._get()

    def put_metadata_schema_directory(self, metadata_schema_directory):
        """Put/update the path to the metadata schema directory.

        The value is updated in the  config file.

        :param metadata_schema_directory: path to the metadata schema directory
        """
        value = os.path.abspath(metadata_schema_directory)
        self._put(value)

    @property
    def metadata_model_names(self):
        """Return list of metadata model names.

        :returns: list of metadata model names
        """
        metadata_schema_directory = self.get_metadata_schema_directory()
        if metadata_schema_directory is None:
            return []
        filenames = os.listdir(metadata_schema_directory)
        return sorted([os.path.splitext(f)[0] for f in filenames])

    def get_metadata_model(self, name):
        """Returns class:`dtool_gui.models.MetadataModel` instance.

        :param name: metadata model name
        :returns: `dtool_gui.models.MetadataModel instance
        """
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
    def is_empty(self):
        """Return True if no metadata schema value has been loaded
        or if the model has been cleared.

        :returns: boolean
        """
        if len(self._metadata_schema_items) == 0:
            return True
        return False

    @property
    def item_names(self):
        """Return metadata names (keys).

        :returns: names of items in the metadata schema
        """
        return sorted(self._metadata_schema_items.keys())

    @property
    def required_item_names(self):
        """Return list of names of required metadata items.

        :returns: names of required items in the metadata schema
        """
        return sorted(list(self._required_item_names))

    @property
    def optional_item_names(self):
        """Return list of names of optional metadata items.

        :returns: names of optional items in the metadata schema
        """
        all_set = set(self.item_names)
        required_set = set(self.required_item_names)
        return sorted(list(all_set - required_set))

    @property
    def selected_optional_item_names(self):
        """Return list of names of selected optional metadata items.

        A :class:`dtool_gui.models.MetadataModel` instance can have optional
        :class:`metadata.MetadataSchemaItem` instances. However for these to be
        included when the dataset metadata is set/updated they need to be
        selected. This property lists the names of the selected optional
        metadata schema items.

        :returns: names of selected optional items in the metadata schema
        """
        return sorted(list(self._selected_optional_item_names))

    @property
    def deselected_optional_item_names(self):
        """Return list of names of deselected optional metadata items.

        Inverse of
        :func:`dtool_gui.models.MetadataModel.selected_optional_item_names`

        :returns: names of deselected optional items in the metadata schema
        """
        optional_set = set(self.optional_item_names)
        selected_set = set(self.selected_optional_item_names)
        return sorted(list(optional_set - selected_set))

    @property
    def in_scope_item_names(self):
        """Return required and selected optional item names.

        :returns: names of required and selected optional items in the metadata
                  schema
        """
        return self.required_item_names + self.selected_optional_item_names

    @property
    def issues(self):
        """Return list of issues with metadata.

        Only reports on issues that are required and optional metadata that has
        been selected. Each value that has been set is evaluated against its
        schema.

        :returns: list of issues
        """
        _issues = []
        for item_name in self.in_scope_item_names:
            schema = self.get_schema(item_name)
            value = self.get_value(item_name)
            if value is not None:
                for i in schema.issues(value):
                    _issues.append((item_name, str(i)))
        return _issues

    def clear(self):
        """Clear the model of existing data."""
        self._metadata_schema_items = {}
        self._metadata_values = {}
        self._required_item_names = set()
        self._selected_optional_item_names = set()

    def load_master_schema(self, master_schema):
        """Load JSON schema of an object describing the metadata model.

        Example of a mater schema::

          {
            "type": "object,
            "properties": {
                "description": {"type:" "string"},
                "project": {"type": "string"}
            }
            "required": ["description"]
        }

        The "type" of the master schema should be "object". The "properties" in
        the master schema are converted to :class:`metadata.MetadataSchemaItem`
        instances. The "required" property is used to classify metadata items
        as required/optional.

        :param master_schema: dictionary containing a JSON schema
        """
        for name, schema in master_schema["properties"].items():
            self._metadata_schema_items[name] = MetadataSchemaItem(schema)

        if "required" in master_schema:
            for r in master_schema["required"]:
                self._required_item_names.add(r)

    def add_metadata_property(self, name, schema={}, required=False):
        """Add a metadata property to the master schema.

        Method to build a build up or extend the master schema.

        :param name: name of the metadata item, the key used in the property
                     dictionary of the master schema
        :param schema: the JSON schema to use to create a
                       :class:`metadata.MetadataSchemaItem`
        :param required: boolean value stating whether the property is required
                         or optional
        """
        self._metadata_schema_items[name] = MetadataSchemaItem(schema)
        if required:
            self._required_item_names.add(name)

    def get_master_schema(self):
        """Return JSON schema of object describing the metadata model.

        :returns: JSON schema representing the current state of the
                  :class:`dtool_gui.models.MetadataModel` as a dictionary
        """
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
        """Return metadata schema.

        :param name: name of the metadata
        :returns: :class:`metadata.MetadataSchemaItem`
        """
        return self._metadata_schema_items[name]

    def get_value(self, name):
        """Return metadata value.

        :param name: name of the metadata
        :returns: the value of the metadata
        """
        if name not in self._metadata_values:
            return None
        return self._metadata_values[name]

    def set_value(self, name, value):
        """Set the metadata value.

        :param name: name of the metadata
        :param value: value to set the metadata to
        """
        self._metadata_values[name] = value

    def set_value_from_str(self, name, value_as_str):
        """Set the metadata value from a string forcing the type.

        :param name: name of the metadata
        :param value_as_str: string representing the value of the metadata
        """
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
        """Validate the metadata value against its schema.

        :param name: name of the metadata
        :returns: True if the value is valid
        """
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


class DataSetModel(object):
    "Model for working with a frozen dataset."

    def __init__(self):
        self._dataset = None
        self._metadata_model = None

    @property
    def name(self):
        """Return the name of the loaded dataset.

        :returns: name of the dataset or None of the dataset has not been set
        """
        if self._dataset is None:
            return None
        return self._dataset.name

    @property
    def metadata_model(self):
        """Return the metadata model.

        :returns: :class:`dtool_gui.models.MetadataModel` instance
        """
        return self._metadata_model

    @property
    def is_empty(self):
        """Return True if no dataset has been loaded or if the model has been cleared.

        :returns: boolean
        """
        if self._dataset is None:
            return True
        return False

    def clear(self):
        """Clear the model of existing data."""
        self._dataset = None
        self._metadata_model = None

    def load_dataset(self, uri):
        """Load the dataset from a URI.

        :param uri: URI to a dtoolcore.DataSet
        """
        logger.info("{} loading dataset from URI: {}".format(self, uri))
        self.clear()
        self._dataset = dtoolcore.DataSet.from_uri(uri)
        self._metadata_model = metadata_model_from_dataset(self._dataset)

    def update_name(self, name):
        """Update the name of the dataset.

        :param name: new dataset name
        """
        self._dataset.update_name(name)

    def update_metadata(self):
        """Update dataset with any changes made to the metadata model.

        Sets all the metadata for all
        :attr:`dtool_gui.models.MetadataModel.in_scope_item_names`

        Both the dataset readme and annotations are updated.

        :raises dtool_gui.models.MetadataValidationError: if the metadata value
            is not valid according to its schema
        :raises dtool_gui.models.MissingRequiredMetadataError: if a required
            metadata value has not been set
        """

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

        readme_lines = ["---"]
        for key in self.metadata_model.in_scope_item_names:
            value = self.metadata_model.get_value(key)
            self._dataset.put_annotation(key, value)
            readme_lines.append("{}: {}".format(key, value))
        readme_content = "\n".join(readme_lines)
        self._dataset.put_readme(readme_content)

        # Update _metadata_schema annotation.
        metadata_schema = self.metadata_model.get_master_schema()
        self._dataset.put_annotation(
            METADATA_SCHEMA_ANNOTATION_NAME,
            metadata_schema
        )


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
        """Return the name to use for the dataset.

        :returns: name of the dataset or None if it has not been set
        """
        return self._name

    @property
    def base_uri(self):
        """Return the base URI for the dataset.

        :returns: base URI or None if it has not been set
        """
        return self._base_uri_model.get_base_uri()

    @property
    def input_directory(self):
        """Return the path to the input directory.

        :returns: input data directory path or None if it has not been set
        """
        return self._input_directory

    @property
    def metadata_model(self):
        """Return the metadata model.

        :returns: :class:`dtool_gui.models.MetadataModel` instance or None if
                  it has not been set
        """
        return self._metadata_model

    @property
    def uri(self):
        """Return the URI of the created dataset.

        :returns: dataset URI or None if it has not been set
        """
        return self._uri

    def _yield_path_handle_tuples(self):
        path_length = len(self.input_directory) + 1

        for dirpath, dirnames, filenames in os.walk(self.input_directory):
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                handle = path[path_length:]
                if dtoolcore.utils.IS_WINDOWS:
                    handle = dtoolcore.utils.windows_to_unix_path(handle)  # NOQA
                yield (path, handle)

    def set_name(self, name):
        """Set the name to use for the dataset.

        :param name: dataset name
        """
        self._name = name

    def set_input_directory(self, input_directory):
        """Set the input directory for the dataset creation process.

        :param input_directory: path to the input directory
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

        :param base_uri_model: :class:`dtool_gui.models.LocalBaseURIModel`
        """
        self._base_uri_model = base_uri_model

    def set_metadata_model(self, metadata_model):
        """Set the metadata model.

        :param metadata_model: :class:`dtool_gui.models.MetadataModel`
        """
        self._metadata_model = metadata_model

    def create(self):
        """Create the dataset in the base URI.

        :raises dtool_gui.models.MissingInputDirectoryError: if the input
            directory has not been set
        :raises dtool_gui.models.MissingDataSetNameError: if the dataset name
            has not been set.
        :raises dtool_gui.models.MissingBaseURIModelError: if the base URI
            model has not been set.
        :raises dtool_gui.models.MissingMetadataModelError: if the metadata
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

            # Add the metadata schema.
            metdata_schema = self.metadata_model.get_master_schema()
            ds_creator.put_annotation(
                METADATA_SCHEMA_ANNOTATION_NAME,
                metdata_schema
            )

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
        """Return base URI.

        :returns: base UIR
        """
        if self._base_uri_model is None:
            return None
        return self._base_uri_model.get_base_uri()

    @property
    def names(self):
        """Return list of dataset names.

        :returns: list of dataset names
        """
        return [ds.name for ds in self._datasets]

    def set_base_uri_model(self, base_uri_model):
        """Set the base URI model.

        :param base_uri_model: dtool_gui.models.LocalBaseURIModel
        """
        self._base_uri_model = base_uri_model
        if self._base_uri_model.get_base_uri() is not None:
            self.reindex()

    def get_uri(self, index):
        """Return the URI of the dataset at a specific index in the list.

        :param index: position of dataset in list
        """
        return self._datasets[index].uri

    def reindex(self):
        """Index the base URI."""
        self._datasets = []
        base_uri = self._base_uri_model.get_base_uri()
        if base_uri is None:
            return
        for ds in dtoolcore.iter_datasets_in_base_uri(base_uri):
            self._datasets.append(ds)

    def yield_properties(self):
        """Return iterable that yields dictionaries with dataset properties."""
        for ds in self._datasets:
            # This is a hack.
            yield _dataset_info(ds)