import parse
import pytest

"""
TODO
Check that sheet initializes correctly, check each attribute for correctness.
Need path(str), sheet_name(str), required_columns(tuple), unique_columns(tuple) for args.
All args but path can be found specified in main for each type of object. Should check initialization
for each type to be extensive. Also check for cases of empty sheets, and skipping rows.
"""


def test_sheet_init():
    pass


def test_sheet_init_skips():
    pass


def test_sheet_init_empty():
    pass


"""
TODO
Input various keys and values to check each if statement
"""


def test_skip_columns():
    pass


"""
TODO
Make row and column to be used. Check if return is as expected
"""


def test_get_cell_info():
    pass


"""
TODO 
Create all inputs that point to some type of parent, then check return against expectation.
Need parsed_object(dictionary), column_type_list(list), column_key_list(list), return(dictionary).
Make test for more than one level of nesting.
"""


def test_get_parent_info():
    pass


"""
TODO 
Will have to create a parsed parent object and cell_info dict to be passed in.
Check to see if the parsed parent object is correctly mutated.
"""


def test_parse_cell_info():
    pass


"""
TODO 
Input row and check for appropriate tuple returned
"""


def test_get_unique_row_key():
    pass


"""
TODO 
input str with various symbols that we want to get rid of and test against
the expected clean str. One test w/multiple strs should be fine
"""


def test_clean_keys():
    pass
