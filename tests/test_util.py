import src.util as util
import pytest
from tests.cases.case_util import *


@pytest.mark.parametrize("value, expected", case_standardize_name)
def test_standardize_name(value, expected):
    actual = util.standardize_name(value)
    if expected is None:
        assert actual is None, f"Expected Value: {expected}, Actual Value: {actual}"
    elif pd.isna(expected):
        assert pd.isna(actual), f"Expected Value: {expected}, Actual Value: {actual}"
    else:
        assert actual == expected, f"Expected Value: {expected}, Actual Value: {actual}"


@pytest.mark.parametrize("required_col_list, expected", case_filter_required_col)
def test_filter_required_col(required_col_list, expected):
    actual = util.filter_required_col(required_col_list)
    assert all(
        [a == b for a, b in zip(actual, expected)]
    ), f"Expected Value: {expected}, Actual Value: {actual}"


@pytest.mark.parametrize(
    "exe_dir, file_name, expected_dict_len, expected_bool", case_read_config
)
def test_read_config(exe_dir, file_name, expected_dict_len, expected_bool):
    actual_dict, actual_bool = util.read_config(exe_dir, file_name)
    assert (
        len(actual_dict) == expected_dict_len
    ), f"Expected Dict Length: {expected_dict_len}, Actual Dict Length: {len(actual_dict)}"
    assert (
        actual_bool == expected_bool
    ), f"Expected Bool: {expected_bool}, Actual Bool: {actual_bool}"
