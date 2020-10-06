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
            "project": {"type": "string", "minLenght": 3, "maxLength": 80},
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

    metadata_model.set_value("project", "dtool-gui")
    assert metadata_model.get_value("project") == "dtool-gui"
