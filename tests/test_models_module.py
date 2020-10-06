"""Test the dtool-gui (MVC) models."""

import os

from . import tmp_dir_fixture  # NOQA


def test_LocalBaseURIModel(tmp_dir_fixture):  # NOQA

    from models import LocalBaseURIModel

    config_path = os.path.join(tmp_dir_fixture, "config.json")
    assert not os.path.isfile(config_path)

    base_uri_path = os.path.join(tmp_dir_fixture, "datasets")

    base_uri_model = LocalBaseURIModel(config_path=config_path)
    assert base_uri_model.get_base_uri() is None

    base_uri_model.put_base_uri(base_uri_path)
    assert os.path.isfile(config_path)

    another_base_uri_model = LocalBaseURIModel(config_path=config_path)
    assert another_base_uri_model.get_base_uri() == base_uri_path


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
