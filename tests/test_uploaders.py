import os

import pytest
import cript as C
from src.uploaders import *
from tests.cases.case_uploaders import *
from tests.fixtures import *


class TestUploaders:
    def test_connect_true(self, fixture_read_config):
        _config_key_dict = fixture_read_config
        BASE_URL = _config_key_dict.get("BASE_URL")
        TOKEN = _config_key_dict.get("TOKEN")
        try:
            actual = C.API(BASE_URL, TOKEN)
        except Exception:
            actual = None
        assert (
            actual is not None
        ), "Fail to connect to database, have a check on config.json"

    @pytest.mark.parametrize("base_url, token, expected", case_connect_false)
    def test_connect_false(self, base_url, token, expected):
        with pytest.raises(expected) as excinfo:
            connect(base_url, token)
        assert (
            excinfo.type == expected
        ), f"Expected Error: {expected}, Actual Value: {excinfo.type}"

    def test_get_group_true(self, fixture_read_config, fixture_connect):
        _config_key_dict = fixture_read_config
        db = fixture_connect
        group_name = _config_key_dict.get("GROUP")
        actual = None
        try:
            actual = get_group(db, group_name)
        except Exception:
            pass
        assert isinstance(
            actual, C.Group
        ), f"Expected Type: {C.Group}, Actual Type: {type(actual)}"
        assert (
            actual.name == group_name
        ), f"Expected Name: {group_name}, Actual Value: {actual.name}"

    @pytest.mark.parametrize("group_name, expected_error", case_get_group_false)
    def test_get_group_false(self, group_name, expected_error, fixture_connect):
        db = fixture_connect
        if db is not None:
            with pytest.raises(expected_error) as excinfo:
                get_group(db, group_name)
            assert (
                excinfo.type == expected_error
            ), f"Expected Error: {expected_error}, Actual Error: {excinfo.type}"

    def test_get_collection_true(
        self, fixture_read_config, fixture_connect, fixture_get_group
    ):
        _config_key_dict = fixture_read_config
        db = fixture_connect
        group_obj = fixture_get_group
        collection_name = _config_key_dict.get("COLLECTION")
        actual = None
        try:
            actual = get_collection(db, group_obj, collection_name)
        except Exception:
            pass
        assert isinstance(
            actual, C.Collection
        ), f"Expected Type: {C.Collection}, Actual Type: {type(actual)}"
        assert (
            actual.name == collection_name
        ), f"Expected Name: {collection_name}, Actual Value: {actual.name}"

    @pytest.mark.parametrize(
        "collection_name, expected_error", case_get_collection_false
    )
    def test_get_collection_false(
        self, collection_name, expected_error, fixture_connect, fixture_get_group
    ):
        db = fixture_connect
        group_obj = fixture_get_group
        if db is not None and group_obj is not None:
            with pytest.raises(expected_error) as excinfo:
                get_collection(db, group_obj, collection_name)
            assert (
                excinfo.type == expected_error
            ), f"Expected Error: {expected_error}, Actual Error: {excinfo.type}"
