import os

import pytest
import cript as C
from src.uploaders import connect
from src.util import read_config


def fixture_read_config():
    dir_path = os.path.abspath(os.path.dirname(__file__))
    file_name = "config-test.json"
    _config_key_dict, _config_is_found = read_config(dir_path, file_name)
    return _config_key_dict


def fixture_connect():
    _config_key_dict = fixture_read_config()
    BASE_URL = _config_key_dict.get("BASE_URL")
    TOKEN = _config_key_dict.get("TOKEN")
    return connect(BASE_URL, TOKEN)


def fixture_get_group():
    _config_key_dict = fixture_read_config()
    db = fixture_connect()
    GROUP = _config_key_dict.get("GROUP")
    group_obj = db.get(C.Group, {"name": GROUP})
    return group_obj


def fixture_get_collection():
    _config_key_dict = fixture_read_config()
    db = fixture_connect()
    group_obj = fixture_get_group()
    COLLECTION = _config_key_dict.get("COLLECTION")
    collection_obj = db.get(C.Collection, {"name": COLLECTION, "group": group_obj.uid})
    return collection_obj
