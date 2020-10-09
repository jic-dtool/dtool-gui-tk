"Functional tests showing how models can be used to create/edit datasets."

import os

from . import tmp_dir_fixture  # NOQA

import pytest


def test_create_dataset(tmp_dir_fixture):  # NOQA

    import models

    input_directory = os.path.join(tmp_dir_fixture, "input_directory")
    os.mkdir(input_directory)
    with open(os.path.join(input_directory, "data.txt"), "w") as fh:
        fh.write("my data in a file")

    base_uri_directory = os.path.join(tmp_dir_fixture, "datasets")
    os.mkdir(base_uri_directory)
    config_path = os.path.join(tmp_dir_fixture, "dtool-gui.json")
    base_uri_model = models.LocalBaseURIModel(config_path)
    base_uri_model.put_base_uri(base_uri_directory)

    proto_dataset_model = models.ProtoDataSetModel()

    metadata_model = models.MetadataModel()
    metadata_model.add_metadata_property(
        name="project",
        schema={"type": "string", "maxLength": 10},
        required=True
    )

    with pytest.raises(models.MissingDataSetNameError):
        proto_dataset_model.create()

    proto_dataset_model.set_name("my-dataset")

    with pytest.raises(models.MissingInputDirectoryError):
        proto_dataset_model.create()

    proto_dataset_model.set_input_directory(input_directory)

    with pytest.raises(models.MissingBaseURIModelError):
        proto_dataset_model.create()

    proto_dataset_model.set_base_uri_model(base_uri_model)

    with pytest.raises(models.MissingMetadataModelError):
        proto_dataset_model.create()

    proto_dataset_model.set_metadata_model(metadata_model)

    with pytest.raises(models.MissingRequiredMetadataError):
        proto_dataset_model.create()

    proto_dataset_model.metadata_model.set_value("project", "too-long-project-name")  # NOQA

    with pytest.raises(models.MetadataValidationError):
        proto_dataset_model.create()

    proto_dataset_model.metadata_model.set_value("project", "dtool-gui")

    proto_dataset_model.create()

    expected_uri = dtoolcore.utils.sanitise_uri(
        os.path.join(base_uri_directory, "dtool-gui")
    )
    assert proto_dataset_model.uri == expected_uri
