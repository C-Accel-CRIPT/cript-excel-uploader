import pytest
from src.parser import parse_col_name
from src.errors import ColumnParseError
from tests.cases.case_parser import *


@pytest.mark.parametrize("column_name, expected", case_parse_col_name_true)
def test_parse_col_name_true(column_name, expected):
    assert (
        parse_col_name(column_name) == expected
    ), f"Expected Name: {collection_name}, Actual Value: {actual.name}"


@pytest.mark.parametrize("column_name, expected_error", case_parse_col_name_false)
def test_parse_col_name_false(column_name, expected_error):
    with pytest.raises(ColumnParseError) as excinfo:
        parse_col_name(column_name)
    assert (
        excinfo.type == expected_error
    ), f"Expected Error: {expected_error}, Actual Error: {excinfo.type}"
