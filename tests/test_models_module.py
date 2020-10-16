"""Test the dtool-gui (MVC) models."""

import os

from . import tmp_dir_fixture  # NOQA

import pytest


def test_LocalBaseURIModel(tmp_dir_fixture):  # NOQA

    from models import LocalBaseURIModel
    import dtoolcore.utils

    config_path = os.path.join(tmp_dir_fixture, "config.json")
    assert not os.path.isfile(config_path)

    base_uri_path = os.path.join(tmp_dir_fixture, "datasets")
    base_uri = dtoolcore.utils.sanitise_uri(base_uri_path)

    base_uri_model = LocalBaseURIModel(config_path=config_path)
    assert base_uri_model.get_base_uri() is None

    # Configure the base URI.
    base_uri_model.put_base_uri(base_uri_path)
    assert os.path.isfile(config_path)
    assert base_uri_model.get_base_uri() == base_uri

    another_base_uri_model = LocalBaseURIModel(config_path=config_path)
    assert another_base_uri_model.get_base_uri() == base_uri


def test_MetadataModel():

    from models import MetadataModel

    metadata_model = MetadataModel()

    master_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string", "minLength": 3, "maxLength": 80},
            "species": {
                "type": "string",
                "enum": ["A. australe", "A. barrelieri"]
            },
            "age": {"type": "integer", "minimum": 0, "maximum": 90}
        },
        "required": ["project"]
    }

    metadata_model.load_master_schema(master_schema)

    assert metadata_model.required_item_names == ["project"]

    expected_item_names = sorted(master_schema["properties"].keys())
    assert metadata_model.item_names == expected_item_names

    from metadata import MetadataSchemaItem
    project_schema = master_schema["properties"]["project"]
    project_metadata_schema_item = MetadataSchemaItem(project_schema)
    assert metadata_model.get_schema("project") == project_metadata_schema_item  # NOQA

    # At this point no values for any metadata has been set.
    assert metadata_model.get_value("project") is None

    # Test setting the project.
    metadata_model.set_value("project", "dtool-gui")
    assert metadata_model.get_value("project") == "dtool-gui"

    # Test updating the project.
    metadata_model.set_value("project", "updated-name")
    assert metadata_model.get_value("project") == "updated-name"

    # It is possible to set values that would fail validation.
    metadata_model.set_value("age", "not a number")
    assert metadata_model.get_value("age") == "not a number"

    # It is up to the client to check that the value is valid.
    assert not metadata_model.is_okay("age")

    # Fix the metadata and check again.
    metadata_model.set_value("age", 10)
    assert metadata_model.is_okay("age")

    # Check that generated master schema matches the input master schema.
    assert metadata_model.get_master_schema() == master_schema


def test_MetadataModelSchemaBuilderAPI():

    from models import MetadataModel

    metadata_model = MetadataModel()
    assert metadata_model.required_item_names == []
    assert metadata_model.item_names == []

    # Initially the metadata model has not got any "properties".
    empty_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    assert metadata_model.get_master_schema() == empty_schema

    # Add some "properties" to the master metadata schema.
    project_schema = {"type": "string", "minLength": 3, "maxLength": 80}
    metadata_model.add_metadata_property(
        name="project",
        schema=project_schema,
        required=True
    )
    metadata_model.add_metadata_property(
        name="age",
        schema={"type": "integer", "minimum": 0, "maximum": 90},
        required=False
    )

    assert metadata_model.required_item_names == ["project"]
    assert metadata_model.item_names == ["age", "project"]

    from metadata import MetadataSchemaItem
    project_metadata_schema_item = MetadataSchemaItem(project_schema)
    assert metadata_model.get_schema("project") == project_metadata_schema_item  # NOQA

    populated_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string", "minLength": 3, "maxLength": 80},
            "age": {"type": "integer", "minimum": 0, "maximum": 90}
        },
        "required": ["project"]
    }
    assert metadata_model.get_master_schema() == populated_schema


def test_MetadataModel_selected_API():
    # A MetadataModel can have "optional" meta data items.
    # For these to be used they need to be "selected" first."

    from models import MetadataModel

    metadata_model = MetadataModel()

    master_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string", "minLength": 3, "maxLength": 80},
            "species": {
                "type": "string",
                "enum": ["A. australe", "A. barrelieri"]
            },
            "age": {"type": "integer", "minimum": 0, "maximum": 90}
        },
        "required": ["project"]
    }

    metadata_model.load_master_schema(master_schema)

    # Initially no optional items are selected.
    assert metadata_model.optional_item_names == ["age", "species"]
    assert metadata_model.selected_optional_item_names == []
    assert metadata_model.deselected_optional_item_names == ["age", "species"]

    # Select and optional item.
    metadata_model.select_optional_item("species")
    assert metadata_model.optional_item_names == ["age", "species"]
    assert metadata_model.selected_optional_item_names == ["species"]
    assert metadata_model.deselected_optional_item_names == ["age"]

    # Do nothing quietly if the same action is called again.
    metadata_model.select_optional_item("species")
    assert metadata_model.optional_item_names == ["age", "species"]
    assert metadata_model.selected_optional_item_names == ["species"]
    assert metadata_model.deselected_optional_item_names == ["age"]

    # Deselect an optional item.
    metadata_model.deselect_optional_item("species")
    assert metadata_model.optional_item_names == ["age", "species"]
    assert metadata_model.selected_optional_item_names == []
    assert metadata_model.deselected_optional_item_names == ["age", "species"]

    # Do nothing quietly if the same action is called again.
    metadata_model.deselect_optional_item("species")
    assert metadata_model.optional_item_names == ["age", "species"]
    assert metadata_model.selected_optional_item_names == []
    assert metadata_model.deselected_optional_item_names == ["age", "species"]

    # Required and selected metadata is "in scope" to be processed etc.
    expected = metadata_model.required_item_names + metadata_model.selected_optional_item_names  # NOQA
    assert metadata_model.in_scope_item_names == expected


def test_MetadataModel_issues_API():

    from models import MetadataModel

    metadata_model = MetadataModel()

    master_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string", "minLength": 3, "maxLength": 80},
            "species": {
                "type": "string",
                "enum": ["A. australe", "A. barrelieri"]
            },
            "age": {"type": "integer", "minimum": 0, "maximum": 90}
        },
        "required": ["project"]
    }

    metadata_model.load_master_schema(master_schema)

    metadata_model.set_value("project", "x")
    assert len(metadata_model.issues) == 1
    assert metadata_model.issues[0] == ("project", "'x' is too short")


def test_MetadataModel_str_to_typed():
    from models import MetadataModel, UnsupportedTypeError

    master_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "age": {"type": "integer"},
            "time": {"type": "number"},
            "is_amazing": {"type": "boolean"},
        }
    }
    metadata_model = MetadataModel()
    metadata_model.load_master_schema(master_schema)

    metadata_model.set_value_from_str("project", "test")
    assert isinstance(metadata_model.get_value("project"), str)

    metadata_model.set_value_from_str("age", "2")
    assert isinstance(metadata_model.get_value("age"), int)

    metadata_model.set_value_from_str("time", "5")
    assert isinstance(metadata_model.get_value("time"), float)

    metadata_model.set_value_from_str("is_amazing", "True")
    assert isinstance(metadata_model.get_value("is_amazing"), bool)

    metadata_model.set_value_from_str("project", "")
    assert metadata_model.get_value("project") is None

    # If forced typing fails, set to None.
    metadata_model.set_value_from_str("age", "not-an-integer")
    assert metadata_model.get_value("age") is None

    metadata_model.set_value_from_str("time", "not-a-float")
    assert metadata_model.get_value("time") is None

    metadata_model.set_value_from_str("is_amazing", "not-a-bool")
    assert metadata_model.get_value("is_amazing") is None

    metadata_model.add_metadata_property("not_supported", {"type": "object"})
    with pytest.raises(UnsupportedTypeError):
        metadata_model.set_value_from_str("not_supported", {"age": 3})


def test_ProtoDataSetModel(tmp_dir_fixture):  # NOQA

    from models import ProtoDataSetModel

    proto_dataset_model = ProtoDataSetModel()

    assert proto_dataset_model.name is None
    proto_dataset_model.set_name("my-dataset")
    assert proto_dataset_model.name == "my-dataset"

    assert proto_dataset_model.input_directory is None
    proto_dataset_model.set_input_directory(tmp_dir_fixture)
    assert proto_dataset_model.input_directory == tmp_dir_fixture

    from models import DirectoryDoesNotExistError
    with pytest.raises(DirectoryDoesNotExistError):
        proto_dataset_model.set_input_directory("does not exist")
    assert proto_dataset_model.input_directory == tmp_dir_fixture


def test_DataSetListModel(tmp_dir_fixture):  # NOQA

    from models import DataSetListModel, LocalBaseURIModel

    dataset_list_model = DataSetListModel()
    assert dataset_list_model.base_uri is None

    # Create and configure a base URI and BaseURIModel.
    base_uri_directory = os.path.join(tmp_dir_fixture, "datasets")
    os.mkdir(base_uri_directory)
    config_path = os.path.join(tmp_dir_fixture, "dtool-gui.json")
    base_uri_model = LocalBaseURIModel(config_path)
    base_uri_model.put_base_uri(base_uri_directory)

    # Add the base URI model to the dataset list model.
    base_uri = base_uri_model.get_base_uri()
    dataset_list_model.set_base_uri_model(base_uri_model)
    assert dataset_list_model.base_uri == base_uri

    assert len(dataset_list_model.names) == 0

    # Create three empty datasets in the base URI.
    from dtoolcore import DataSetCreator
    dataset_names = sorted(["ds1", "ds2", "ds3"])
    dataset_uris = {}
    for name in dataset_names:
        with DataSetCreator(name=name, base_uri=base_uri) as ds_creator:
            dataset_uris[name] = ds_creator.uri

    # Need to update the dataset list model for the datasets to be discovered.
    assert len(dataset_list_model.names) == 0

    # Update the dataset_list_model.
    dataset_list_model.reindex()

    # Access list of dataset names.
    assert dataset_list_model.names == dataset_names

    # Get URI from name.
    for i, name in enumerate(dataset_list_model.names):
        assert dataset_list_model.get_uri(i) == dataset_uris[name]


def test_MetadataSchemaListModel(tmp_dir_fixture):  # NOQA

    from models import MetadataSchemaListModel

    config_path = os.path.join(tmp_dir_fixture, "config.json")
    assert not os.path.isfile(config_path)

    metadata_schema_dir = os.path.join(tmp_dir_fixture, "metadata_schemas")
    os.mkdir(metadata_schema_dir)

    metadata_schema_list_model = MetadataSchemaListModel(config_path=config_path)  # NOQA
    assert metadata_schema_list_model.get_metadata_schema_directory() is None
    assert metadata_schema_list_model.metadata_model_names == []

    # Configure the metadata schema directory.
    metadata_schema_list_model.put_metadata_schema_directory(metadata_schema_dir)  # NOQA
    assert os.path.isfile(config_path)
    assert metadata_schema_list_model.get_metadata_schema_directory() == metadata_schema_dir  # NOQA

    another_model = MetadataSchemaListModel(config_path=config_path)
    assert another_model.get_metadata_schema_directory() == metadata_schema_dir

    # Add a schema manually.
    basic_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string"}
        }
    }
    import json
    fpath = os.path.join(metadata_schema_dir, "basic.json")
    with open(fpath, "w") as fh:
        json.dump(basic_schema, fh)

    assert another_model.metadata_model_names == ["basic"]

    # Add another schema manually.
    advanced_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string", "minLength": 6, "maxLength": 80}
        },
        "required": ["project"]
    }
    fpath = os.path.join(metadata_schema_dir, "advanced.json")
    with open(fpath, "w") as fh:
        json.dump(advanced_schema, fh)

    assert another_model.metadata_model_names == ["advanced", "basic"]

    # Test schema retrieval.
    from models import MetadataModel
    advanced_model = MetadataModel()
    advanced_model.load_master_schema(advanced_schema)

    accessed_model = metadata_schema_list_model.get_metadata_model("advanced")  # NOQA
    assert advanced_model == accessed_model
