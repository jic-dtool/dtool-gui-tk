"""Test the dtool-gui (MVC) models."""

import os

from . import tmp_dir_fixture  # NOQA

def test_LocalBaseURIModel(tmp_dir_fixture):

    from models import LocalBaseURIModel

    config_path = os.path.join(tmp_dir_fixture, "config.json")
    assert not os.path.isfile(config_path)

    base_uri_path = os.path.join(tmp_dir_fixture, "datasets")

    base_uri_model = LocalBaseURIModel(config_path=config_path)
    assert base_uri_model.get_base_uri() == None

    base_uri_model.put_base_uri(base_uri_path)
    assert os.path.isfile(config_path)

    another_base_uri_model = LocalBaseURIModel(config_path=config_path)
    assert another_base_uri_model.get_base_uri() == base_uri_path
