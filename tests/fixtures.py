import os

import pytest
import cript as C
from src.uploaders import connect
from src.util import read_config


@pytest.fixture(scope="class")
def fixture_read_config():
    dir_path = os.path.abspath(os.path.dirname(__file__))
    file_name = "config-test.json"
    _config_key_dict, _config_is_found = read_config(dir_path, file_name)
    return _config_key_dict


@pytest.fixture(scope="class")
def fixture_connect(fixture_read_config):
    _config_key_dict = fixture_read_config
    BASE_URL = _config_key_dict.get("BASE_URL")
    TOKEN = _config_key_dict.get("TOKEN")
    return connect(BASE_URL, TOKEN)


@pytest.fixture(scope="class")
def fixture_get_group(fixture_read_config, fixture_connect):
    _config_key_dict = fixture_read_config
    db = fixture_connect
    GROUP = _config_key_dict.get("GROUP")
    return db.get(C.Group, {"name": GROUP})


@pytest.fixture(scope="class")
def fixture_get_collection(fixture_read_config, fixture_connect, fixture_get_group):
    _config_key_dict = fixture_read_config
    db = fixture_connect
    group_obj = fixture_get_group
    COLLECTION = _config_key_dict.get("COLLECTION")
    return db.get(C.Collection, {"name": COLLECTION, "group": group_obj})
