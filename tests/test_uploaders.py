import os
import pytest
import cript as C
from src.uploaders import (
    connect,
    get_group,
    get_collection,
    upload,
)
from tests.cases.case_uploaders import (
    BASE_URL,
    TOKEN,
    GROUP,
    COLLECTION,
    db,
    group_obj,
    collection_obj,
    case_connect_false,
    case_get_group_false,
    case_get_collection_false,
)


def test_connect_true():
    try:
        actual = C.API(BASE_URL, TOKEN)
    except Exception:
        actual = None
    assert (
        actual is not None
    ), "Fail to connect to database, have a check on config.json"


@pytest.mark.parametrize("host, token, expected", case_connect_false)
def test_connect_false(host, token, expected):
    with pytest.raises(expected) as excinfo:
        connect(host, token)
    assert (
        excinfo.type == expected
    ), f"Expected Error: {expected}, Actual Value: {excinfo.type}"


def test_get_group_true():
    actual = None
    try:
        actual = get_group(db, GROUP)
    except Exception:
        pass
    assert isinstance(
        actual, C.Group
    ), f"Expected Type: {C.Group}, Actual Type: {type(actual)}"
    assert actual.name == GROUP, f"Expected Name: {GROUP}, Actual Value: {actual.name}"


@pytest.mark.parametrize("group_name, expected_error", case_get_group_false)
def test_get_group_false(group_name, expected_error):
    if db is not None:
        with pytest.raises(expected_error) as excinfo:
            get_group(db, group_name)
        assert (
            excinfo.type == expected_error
        ), f"Expected Error: {expected_error}, Actual Error: {excinfo.type}"


def test_get_collection_true():
    actual = None
    try:
        actual = get_collection(db, group_obj, COLLECTION)
    except Exception:
        pass
    assert isinstance(
        actual, C.Collection
    ), f"Expected Type: {C.Collection}, Actual Type: {type(actual)}"
    assert (
        actual.name == COLLECTION
    ), f"Expected Name: {COLLECTION}, Actual Value: {actual.name}"

    @pytest.mark.parametrize(
        "collection_name, expected_error", case_get_collection_false
    )
    def test_get_collection_false(collection_name, expected_error):
        if db is not None and group_obj is not None:
            with pytest.raises(expected_error) as excinfo:
                get_collection(db, group_obj, collection_name)
            assert (
                excinfo.type == expected_error
            ), f"Expected Error: {expected_error}, Actual Error: {excinfo.type}"
