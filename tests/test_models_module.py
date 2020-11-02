"""Test the dtool-gui (MVC) models."""

import os

from . import tmp_dir_fixture  # NOQA

import pytest


def test_LocalBaseURIModel(tmp_dir_fixture):  # NOQA

    from dtool_gui.models import LocalBaseURIModel
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

    from dtool_gui.models import MetadataModel

    metadata_model = MetadataModel()

    assert metadata_model.is_empty

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

    assert not metadata_model.is_empty

    assert metadata_model.required_item_names == ["project"]

    expected_item_names = sorted(master_schema["properties"].keys())
    assert metadata_model.item_names == expected_item_names

    from dtool_gui.metadata import MetadataSchemaItem
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

    # Test clearing metadata model.
    metadata_model.clear()
    assert metadata_model.is_empty


def test_MetadataModelSchemaBuilderAPI():

    from dtool_gui.models import MetadataModel

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

    from dtool_gui.metadata import MetadataSchemaItem
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

    from dtool_gui.models import MetadataModel

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

    from dtool_gui.models import MetadataModel

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
    from dtool_gui.models import MetadataModel, UnsupportedTypeError

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

    from dtool_gui.models import ProtoDataSetModel

    proto_dataset_model = ProtoDataSetModel()

    assert proto_dataset_model.name is None
    proto_dataset_model.set_name("my-dataset")
    assert proto_dataset_model.name == "my-dataset"

    assert proto_dataset_model.input_directory is None
    proto_dataset_model.set_input_directory(tmp_dir_fixture)
    assert proto_dataset_model.input_directory == tmp_dir_fixture

    from dtool_gui.models import DirectoryDoesNotExistError
    with pytest.raises(DirectoryDoesNotExistError):
        proto_dataset_model.set_input_directory("does not exist")
    assert proto_dataset_model.input_directory == tmp_dir_fixture


def test_DataSetListModel(tmp_dir_fixture):  # NOQA

    from dtool_gui.models import DataSetListModel, LocalBaseURIModel

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

    # Test yield_properties.
    props_generator = dataset_list_model.yield_properties()
    try:
        from collections.abc import Iterable
    except ImportError:
        from collections import Iterable
    assert isinstance(props_generator, Iterable)
    first = next(props_generator)
    assert "name" in first


def test_MetadataSchemaListModel(tmp_dir_fixture):  # NOQA

    from dtool_gui.models import MetadataSchemaListModel

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
    from dtool_gui.models import MetadataModel
    advanced_model = MetadataModel()
    advanced_model.load_master_schema(advanced_schema)

    accessed_model = metadata_schema_list_model.get_metadata_model("advanced")  # NOQA
    assert advanced_model == accessed_model


def test_DataSetModel_basic(tmp_dir_fixture):  # NOQA

    # Create an empty dataset model.
    from dtool_gui.models import DataSetModel
    dataset_model = DataSetModel()
    assert dataset_model.name is None
    assert dataset_model.metadata_model is None

    assert dataset_model.is_empty

    # Create a dataset.
    from dtoolcore import DataSetCreator
    dataset_name = "my-dataset"
    annotations = {"project": "my-project", "description": "my-description"}
    readme_lines = ["---"]
    with DataSetCreator(
        name=dataset_name,
        base_uri=tmp_dir_fixture
    ) as ds_creator:
        for key in sorted(annotations.keys()):
            value = annotations[key]
            ds_creator.put_annotation(key, value)
            readme_lines.append("{}: {}".format(key, value))
        readme = "\n".join(readme_lines)
        ds_creator.put_readme(readme)
        uri = ds_creator.uri

    dataset_model.load_dataset(uri)
    assert not dataset_model.is_empty

    # Check that it has the right properties.
    assert dataset_model.name == dataset_name
    expected_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["description", "project"]
    }
    assert dataset_model.metadata_model.get_master_schema() == expected_schema
    for key in annotations.keys():
        assert dataset_model.metadata_model.get_value(key) == annotations[key]

    # Check that one can update the properties on the actual dataset.
    from dtoolcore import DataSet
    dataset_model.update_name("new-name")
    assert dataset_model.name == "new-name"

    dataset = DataSet.from_uri(uri)
    assert dataset.name == "new-name"

    dataset_model.metadata_model.set_value("project", "new-project")
    assert dataset_model.metadata_model.get_value("project") == "new-project"

    # Updating the metadata in the metadata model requires a call to
    # DataSetModel.update_metadata()
    assert dataset.get_annotation("project") == "my-project"
    dataset_model.update_metadata()
    assert dataset.get_annotation("project") == "new-project"

    # DataSetModel.update_metadata() should raise MissingRequiredMetadataError
    # and MetadataValidationError if appropriate.
    from dtool_gui.models import (
        MissingRequiredMetadataError,
        MetadataValidationError
    )

    # Add new required metadata property,
    # but don't set it so that it is missing.
    dataset_model.metadata_model.add_metadata_property(
        name="age",
        schema={"type": "integer", "exclusiveMinimum": 0},
        required=True
    )
    with pytest.raises(MissingRequiredMetadataError):
        dataset_model.update_metadata()

    # Set the age metadata to an invalid value.
    dataset_model.metadata_model.set_value("age", -1)
    with pytest.raises(MetadataValidationError):
        dataset_model.update_metadata()

    # Test with valid value.
    # Set the age metadata to an invalid value.
    dataset_model.metadata_model.set_value("age", 1)
    dataset_model.update_metadata()
    assert dataset.get_annotation("age") == 1

    # When the dataset is updated the special _metadata_schema annotation is
    # also updated.
    expected_schema = dataset_model.metadata_model.get_master_schema()
    assert dataset.get_annotation("_metadata_schema") == expected_schema

    # If the metadata model is missing DataSetModel.update_metadata
    # should raise MissingMetadataModelError.
    from dtool_gui.models import MissingMetadataModelError
    dataset_model._metadata_model = None
    with pytest.raises(MissingMetadataModelError):
        dataset_model.update_metadata()

    # Test clearing the DataSetModel.
    dataset_model.clear()
    assert dataset_model.is_empty


def test_DataSetModel_update_metadata_works_on_annotations_and_readme(tmp_dir_fixture):  # NOQA

    # Create a basic dataset.
    from dtoolcore import DataSetCreator, DataSet
    with DataSetCreator("my-dataset", tmp_dir_fixture) as ds_creator:
        ds_creator.put_annotation("project", "test")

    # Create a dataset model from the dataset
    from dtool_gui.models import DataSetModel
    dataset_model = DataSetModel()
    dataset_model.load_dataset(ds_creator.uri)

    # Add an optional metadata and set it.
    dataset_model.metadata_model.add_metadata_property("age", {"type": "integer"})  # NOQA
    dataset_model.metadata_model.set_value("age", 3)
    dataset_model.metadata_model.select_optional_item("age")

    # Load the dataset.
    dataset = DataSet.from_uri(ds_creator.uri)

    # Dataset before metadata update.
    expected_readme = ""
    assert dataset.get_readme_content() == expected_readme
    expected_annotation_keys = ["project"]
    assert dataset.list_annotation_names() == expected_annotation_keys  # NOQA

    # Update the metadata.
    dataset_model.update_metadata()

    # Dataset after metadata update.
    expected_readme = "---\nproject: test\nage: 3"
    assert dataset.get_readme_content() == expected_readme
    expected_annotation_keys = ["_metadata_schema", "age", "project"]
    assert dataset.list_annotation_names() == expected_annotation_keys  # NOQA

def test_json_schema_from_dataset_only_readme(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet, DataSetCreator
    from dtool_gui.models import metadata_model_from_dataset, MetadataModel

    # Only readme.
    readme = "---\nproject: test\nage: 3\ntemperature: 25.5"
    with DataSetCreator("only-readme", tmp_dir_fixture, readme) as ds_creator:
        uri = ds_creator.uri
    dataset = DataSet.from_uri(uri)

    # Create expected metadata model.
    expected_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "age": {"type": "integer"},
            "temperature": {"type": "number"}
        },
        "required": ["age", "project", "temperature"]
    }
    expected_metadata_model = MetadataModel()
    expected_metadata_model.load_master_schema(expected_schema)
    expected_metadata_model.set_value("project", "test")
    expected_metadata_model.set_value("age", 3)
    expected_metadata_model.set_value("temperature", 25.5)

    assert metadata_model_from_dataset(dataset) == expected_metadata_model


def test_json_schema_from_dataset_only_annotations(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet, DataSetCreator
    from dtool_gui.models import metadata_model_from_dataset, MetadataModel

    with DataSetCreator("only-annotations", tmp_dir_fixture) as ds_creator:
        ds_creator.put_annotation("an-int", 3)
        ds_creator.put_annotation("a-float", 3.5)
        ds_creator.put_annotation("a-string", "hello")
        ds_creator.put_annotation("a-bool", True)
        uri = ds_creator.uri
    dataset = DataSet.from_uri(uri)

    # Create expected metadata model.
    expected_schema = {
        "type": "object",
        "properties": {
            "an-int": {"type": "integer"},
            "a-float": {"type": "number"},
            "a-string": {"type": "string"},
            "a-bool": {"type": "boolean"}
        },
        "required": ["an-int", "a-float", "a-string", "a-bool"]
    }
    expected_metadata_model = MetadataModel()
    expected_metadata_model.load_master_schema(expected_schema)
    expected_metadata_model.set_value("an-int", 3)
    expected_metadata_model.set_value("a-float", 3.5)
    expected_metadata_model.set_value("a-string", "hello")
    expected_metadata_model.set_value("a-bool", True)

    actual_metadata_model = metadata_model_from_dataset(dataset)
    assert actual_metadata_model.item_names == expected_metadata_model.item_names  # NOQA
    assert actual_metadata_model.required_item_names == expected_metadata_model.required_item_names  # NOQA
    for name in expected_metadata_model.item_names:
        expected_schema = expected_metadata_model.get_schema(name)
        actual_schema = actual_metadata_model.get_schema(name)
        assert expected_schema == actual_schema
        expected_value = expected_metadata_model.get_value(name)
        actual_value = actual_metadata_model.get_value(name)
        assert expected_value == actual_value

    assert metadata_model_from_dataset(dataset) == expected_metadata_model

    # Unsupported type.
    from dtool_gui.models import UnsupportedTypeError
    with DataSetCreator("unsupported-type", tmp_dir_fixture) as ds_creator:
        ds_creator.put_annotation("complex-object", {"x": 1, "y": 2})
        ds_creator.put_annotation("an-int", 3)
        uri = ds_creator.uri
    dataset = DataSet.from_uri(uri)
    with pytest.raises(UnsupportedTypeError):
        metadata_model_from_dataset(dataset)


def test_json_schema_from_dataset_readme_and_annotations_diverse_not_conflicting(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet, DataSetCreator
    from dtool_gui.models import metadata_model_from_dataset, MetadataModel

    # Diverse but not conflicting.
    readme = "---\nproject: test"
    with DataSetCreator("readme-and-annotations", tmp_dir_fixture, readme) as ds_creator:  # NOQA
        ds_creator.put_annotation("age", 3)
        uri = ds_creator.uri
    dataset = DataSet.from_uri(uri)

    # Create expected metadata model.
    expected_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["age", "project"]
    }
    expected_metadata_model = MetadataModel()
    expected_metadata_model.load_master_schema(expected_schema)
    expected_metadata_model.set_value("project", "test")
    expected_metadata_model.set_value("age", 3)

    actual_metadata_model = metadata_model_from_dataset(dataset)
    assert actual_metadata_model == expected_metadata_model


def test_json_schema_from_dataset_readme_and_annotations_conflicting(tmp_dir_fixture):  # NOQA

    from dtoolcore import DataSet, DataSetCreator
    from dtool_gui.models import metadata_model_from_dataset
    # Identical but missing type.
    readme = "---\nproject: test\nage: 4"
    with DataSetCreator("readme-and-annotations", tmp_dir_fixture, readme) as ds_creator:  # NOQA
        ds_creator.put_annotation("age", 3)
        uri = ds_creator.uri
    dataset = DataSet.from_uri(uri)

    from dtool_gui.models import MetadataConflictError
    with pytest.raises(MetadataConflictError):
        metadata_model_from_dataset(dataset)


def test_json_schema_from_dataset_schema_annotation(tmp_dir_fixture):  # NOQA
    # Create a master metadata schema.
    metadata_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["project"]
    }

    # Create a dataset.
    from dtoolcore import DataSet, DataSetCreator
    with DataSetCreator("annotation-schema", tmp_dir_fixture) as ds_creator: # NOQA
        ds_creator.put_annotation("_metadata_schema", metadata_schema)
    dataset = DataSet.from_uri(ds_creator.uri)

    # Create the expected model from the schema.
    from dtool_gui.models import MetadataModel
    expected_metadata_model = MetadataModel()
    expected_metadata_model.load_master_schema(metadata_schema)

    # Test that the function returns the correct model.
    from dtool_gui.models import metadata_model_from_dataset
    actual_metadata_model = metadata_model_from_dataset(dataset)
    assert actual_metadata_model == expected_metadata_model


def test_json_schema_from_dataset_schema_annotation_with_conflicting_type_in_readme_and_annotations(tmp_dir_fixture):  # NOQA
    # Create a master metadata schema.
    metadata_schema = {
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["project"]
    }

    # Create a dataset.
    from dtoolcore import DataSet, DataSetCreator
    readme = "---\nproject: 1"  # Type is integer instead of string.
    with DataSetCreator("annotation-schema", tmp_dir_fixture, readme) as ds_creator: # NOQA
        ds_creator.put_annotation("_metadata_schema", metadata_schema)
        ds_creator.put_annotation("age", "old")  # Type is string instead of integer  # NOQA
    dataset = DataSet.from_uri(ds_creator.uri)

    # Create the expected model from the schema.
    from dtool_gui.models import MetadataModel
    expected_metadata_model = MetadataModel()
    expected_metadata_model.load_master_schema(metadata_schema)
    expected_metadata_model.set_value("project", 1)  # Expecting incorrect type.  # NOQA
    expected_metadata_model.set_value("age", "old")  # Expecting incorrect type.  # NOQA

    # Test that the function returns the correct model.
    from dtool_gui.models import metadata_model_from_dataset
    actual_metadata_model = metadata_model_from_dataset(dataset)
    assert actual_metadata_model == expected_metadata_model
