import pandas as pd
import src.parse as parse
import pytest

sheet_parameters = {
    "experiment": {
        "name": "experiment",
        "required_columns": ("name",),
        "unique_columns": ("name",),
    },
    "citation": {
        "name": "citation",
        "required_columns": ("title",),
        "unique_columns": ("title",),
    },
    "data": {
        "name": "data",
        "required_columns": ("experiment", "name", "type", "path"),
        "unique_columns": ("name",),
    },
    "material": {
        "name": "material",
        "required_columns": ("name",),
        "unique_columns": ("name",),
    },
    "mixture component": {
        "name": "mixture component",
        "required_columns": ("mixture", "material"),
        "unique_columns": ("mixture", "material"),
    },
    "process": {
        "name": "process",
        "required_columns": ("experiment", "name", "type"),
        "unique_columns": ("name",),
    },
    "prerequisite process": {
        "name": "prerequisite process",
        "required_columns": ("process", "prerequisite"),
        "unique_columns": ("process", "prerequisite"),
    },
    "process ingredient": {
        "name": "process ingredient",
        "required_columns": ("process", "materials", "keyword"),
        "unique_columns": ("process", "material", "keyword"),
    },
    "process product": {
        "name": "process product",
        "required_columns": ("process", "material"),
        "unique_columns": ("process", "material"),
    },
    "process equipment": {
        "name": "process equipment",
        "required_columns": ("process", "key"),
        "unique_columns": ("process", "key"),
    },
}

path = "testing_template_v0.xlsx"

"""
TODO
Check that sheet initializes correctly, check each attribute for correctness.
Need path(str), sheet_name(str), required_columns(tuple), unique_columns(tuple) for args.
All args but path can be found specified in main for each type of object.
Also check for cases of empty sheets, and skipping rows.
"""


def test_sheet_init():
    exp_params = sheet_parameters["experiment"]
    sheet = parse.Sheet(
        path,
        exp_params["name"],
        exp_params["required_columns"],
        exp_params["unique_columns"],
    )
    correctMI = pd.MultiIndex.from_tuples(
        [("attribute", "*name", " "), ("attribute", "notes", "Unnamed: 1_level_2")]
    )
    assert sheet.path == path
    assert sheet.sheet_name == exp_params["name"]
    assert sheet.required_columns == exp_params["required_columns"]
    assert sheet.unique_columns == exp_params["unique_columns"]
    assert (
        sheet.df[("attribute", "*name")].values[0]
        == "Anionic Polymerization of Styrene"
    )
    assert sheet.columns.equals(correctMI) == True


def test_sheet_init_skips():
    mat_params = sheet_parameters["material"]
    sheet = parse.Sheet(
        path,
        mat_params["name"],
        mat_params["required_columns"],
        mat_params["unique_columns"],
    )
    assert len(sheet.df.index) == 9


def test_sheet_init_empty():
    cit_params = sheet_parameters["citation"]
    sheet = parse.Sheet(
        path,
        cit_params["name"],
        cit_params["required_columns"],
        cit_params["unique_columns"],
    )
    assert sheet.exists == False


def test_skip_columns():
    """
    Input various keys and values to check each if statement
    """
    mat_params = sheet_parameters["material"]
    sheet = parse.Sheet(
        path,
        mat_params["name"],
        mat_params["required_columns"],
        mat_params["unique_columns"],
    )
    # Tests skipping #'s
    assert sheet._skip_column("#storage", "my storage") == True
    # Tests not skipping associated even with empty value
    assert sheet._skip_column("associated", None) == False
    # Tests skipping empty values
    assert sheet._skip_column("optical_transparency", None) == True
    # Tests not skipping proper inputs
    assert sheet._skip_column("optical_transparency", 0.5) == False


def test_get_cell_info():
    """
    Make row and column to be used. Check if return is as expected
    """
    # Setup
    mat_params = sheet_parameters["material"]
    sheet = parse.Sheet(
        path,
        mat_params["name"],
        mat_params["required_columns"],
        mat_params["unique_columns"],
    )

    ix1 = 1
    column = ("property", "optical_transparency", "Unnamed")

    ix2 = 2
    column2 = ("property:condition", "density:temperature", "C")

    row = {column: 0.5, column2: 10}
    # Case with no nesting
    correct1 = {
        "index": ix1,
        "nested_types": ["property"],
        "nested_keys": ["optical_transparency"],
        "type": "property",
        "unique_key": "optical_transparency",
        "key": "optical_transparency",
        "value": 0.5,
        "unit": None,
    }
    # Case with nesting
    correct2 = {
        "index": ix2,
        "nested_types": ["property", "condition"],
        "nested_keys": ["density", "temperature"],
        "type": "condition",
        "unique_key": "temperature",
        "key": "temperature",
        "value": 10,
        "unit": "C",
    }
    assert sheet._get_cell_info(ix1, row, column) == correct1
    assert sheet._get_cell_info(ix2, row, column2) == correct2


def test_get_parent():
    """
    Create all inputs that point to some type of parent, then check return against expectation.
    Need parsed_object(dictionary), column_type_list(list), column_key_list(list), return(dictionary).
    Make test for more than one level of nesting.
    """
    parsed_object = {
        "density": {
            "sheet": "material",
            "index": 1,
            "key": "density",
            "value": 10,
            "unit": "g/ml",
            "type": "property",
        }
    }
    # Setup
    mat_params = sheet_parameters["material"]
    sheet = parse.Sheet(
        path,
        mat_params["name"],
        mat_params["required_columns"],
        mat_params["unique_columns"],
    )
    assert sheet._get_parent(
        parsed_object, ["property", "condition"], ["density", "temperature"]
    ) == {
        "sheet": "material",
        "index": 1,
        "key": "density",
        "value": 10,
        "unit": "g/ml",
        "type": "property",
    }
    parsed_object["density"].update(
        {
            "temperature": {
                "sheet": "material",
                "index": 2,
                "key": "temperature",
                "value": 15,
                "unit": "C",
                "type": "condition",
            }
        }
    )
    assert sheet._get_parent(
        parsed_object,
        ["property", "condition", "relation"],
        ["density", "temperature", "data"],
    ) == {
        "sheet": "material",
        "index": 2,
        "key": "temperature",
        "value": 15,
        "unit": "C",
        "type": "condition",
    }


def test_parse_cell():
    """
    Will have to create a parsed parent object and cell_info dict to be passed in.
    Check to see if the parsed parent object is correctly mutated.
    """
    cell_info = {
        "index": 1,
        "nested_types": ["property"],
        "nested_keys": ["optical_transparency"],
        "type": "property",
        "unique_key": "optical_transparency",
        "key": "optical_transparency",
        "value": 0.5,
        "unit": None,
    }
    # Setup
    mat_params = sheet_parameters["material"]
    sheet = parse.Sheet(
        path,
        mat_params["name"],
        mat_params["required_columns"],
        mat_params["unique_columns"],
    )
    parent = {}
    sheet._parse_cell(parent, cell_info)
    assert parent == {
        "optical_transparency": {
            "sheet": "material",
            "index": 1,
            "key": "optical_transparency",
            "value": 0.5,
            "unit": None,
            "type": "property",
        }
    }


def test_get_unique_row_key():
    """
    Input row and check for appropriate tuple returned
    """
    mat_params = sheet_parameters["material"]
    sheet = parse.Sheet(
        path,
        mat_params["name"],
        mat_params["required_columns"],
        mat_params["unique_columns"],
    )
    matKeys = {
        0: ("toluene",),
        1: ("styrene",),
        2: ("1-butanol",),
        3: ("methanol",),
        4: ("polystyrene",),
        5: ("mixture",),
        6: ("component1",),
        8: ("component2",),  # skips index num due to skipping empty row in template
        9: ("intermediate_material_1",),
    }
    for ix, row in sheet.df.iterrows():
        keys = sheet._get_unique_row_key(row)
        assert keys == matKeys[ix]


def test_clean_key():
    """
    input str with various symbols that we want to get rid of and test against
    the expected clean str. One test w/multiple strs should be fine
    """
    raw1 = "[3]temperature"
    raw2 = "*name"
    raw3 = "density    "
    exp_params = sheet_parameters["experiment"]
    sheet = parse.Sheet(
        path,
        exp_params["name"],
        exp_params["required_columns"],
        exp_params["unique_columns"],
    )
    assert sheet._clean_key(raw1) == "temperature"
    assert sheet._clean_key(raw2) == "name"
    assert sheet._clean_key(raw3) == "density"


def test_parse():
    mat_params = sheet_parameters["experiment"]
    sheet = parse.Sheet(
        path,
        mat_params["name"],
        mat_params["required_columns"],
        mat_params["unique_columns"],
    )
    parsed = sheet.parse()
    assert parsed == {
        ("Anionic Polymerization of Styrene",): {
            "name": {
                "sheet": "experiment",
                "index": 0,
                "key": "name",
                "value": "Anionic Polymerization of Styrene",
                "unit": " ",
                "type": "attribute",
            }
        }
    }
