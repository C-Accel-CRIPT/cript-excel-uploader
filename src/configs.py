import cript as C
import inspect
from src.util import filter_required_col

"""
This file is for configs of validation check
"""

# Required columns in every sheet
required_cols = {
    "experiment": filter_required_col(C.Experiment.required),
    "data": filter_required_col(C.Data.required),
    "file": filter_required_col(C.File.required),
    "material": filter_required_col(C.Material.required),
    "mixture component": ["material", "component"],
    "process": filter_required_col(C.Process.required),
    "prerequisite process": ["process", "prerequisite_process"],
    "process ingredient": ["process", "ingredient", "keyword"],
    "process product": ["process", "product"],
}

# Either-or columns in every sheet
either_or_cols = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": [],
    "mixture component": [],
    "process": [],
    "prerequisite process": [],
    "step": [],
    "process ingredient": ["mole", "mass", "volume"],
    "process product": [],
}

# Columns with unique keys should be supported
unique_keys = {
    "experiment": ["name"],
    "data": ["name"],
    "file": [],
    "material": ["name"],
    "mixture component": ["material+component"],
    "process": ["name"],
    "prerequisite process": ["process+prerequisite_process"],
    "process ingredient": ["process+ingredient"],
    "process product": ["process+product"],
}

# Foreign keys, for validation check
foreign_keys = {
    "experiment": ["name"],
    "data": ["experiment", "name"],
    "file": ["data"],
    "material": ["name"],
    "mixture component": ["material", "component"],
    "process": ["experiment", "name"],
    "prerequisite process": ["process", "prerequisite_process"],
    "process ingredient": ["process", "ingredient"],
    "process product": ["process", "product"],
}

# List fields, value in following column is treated as a list separated by coma(",")
list_fields = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": ["names"],
    "mixture component": [],
    "process": ["keywords"],
    "prerequisite process": [],
    "process ingredient": [],
    "process product": [],
}

# Base fields of every node defined in cript sdk
# "node_name": "field"
base_cols = {
    "experiment": inspect.signature(C.Experiment.__init__).parameters,
    "material": inspect.signature(C.Material.__init__).parameters,
    "data": inspect.signature(C.Data.__init__).parameters,
    "file": inspect.signature(C.File.__init__).parameters,
    "process": inspect.signature(C.Process.__init__).parameters,
    "ingredient": inspect.signature(C.Ingredient.__init__).parameters,
    "property": inspect.signature(C.Property.__init__).parameters,
    "condition": inspect.signature(C.Condition.__init__).parameters,
}

# Base node allowed in every sheet
# "sheet_name": "base_node_name"
base_nodes = {
    "experiment": {"experiment"},
    "data": {"data"},
    "file": {"file"},
    "material": {"material"},
    "mixture component": {},
    "process": {"process"},
    "prerequisite process": {},
    "process ingredient": {"ingredient"},
    "process product": {},
}

# Allowed property key in every sheet
sheet_name_to_prop_key = {
    "material": "material-property-key",
    "process": "process-property-key",
}

# Cross validation pair
foreign_key_validation_pairs = [
    {
        "from_field": "experiment",
        "from_sheet_obj": "data",
        "to_field": "name",
        "to_sheet_obj": "experiment",
    },
    {
        "from_field": "data",
        "from_sheet_obj": "file",
        "to_field": "name",
        "to_sheet_obj": "data",
    },
    {
        "from_field": "experiment",
        "from_sheet_obj": "process",
        "to_field": "name",
        "to_sheet_obj": "experiment",
    },
    {
        "from_field": "process",
        "from_sheet_obj": "process ingredient",
        "to_field": "name",
        "to_sheet_obj": "process",
    },
    {
        "from_field": "process",
        "from_sheet_obj": "prerequisite process",
        "to_field": "name",
        "to_sheet_obj": "process",
    },
    {
        "from_field": "prerequisite_process",
        "from_sheet_obj": "prerequisite process",
        "to_field": "name",
        "to_sheet_obj": "process",
    },
    {
        "from_field": "material",
        "from_sheet_obj": "process ingredient",
        "to_field": "name",
        "to_sheet_obj": "material",
    },
    {
        "from_field": "product",
        "from_sheet_obj": "process product",
        "to_field": "name",
        "to_sheet_obj": "material",
    },
    {
        "from_field": "material",
        "from_sheet_obj": "mixture component",
        "to_field": "name",
        "to_sheet_obj": "material",
    },
    {
        "from_field": "component",
        "from_sheet_obj": "mixture component",
        "to_field": "name",
        "to_sheet_obj": "material",
    },
]

# Column name, allowed nesting type
allowed_field_nesting = {
    "base": {None, "prop", "cond", "data"},
    "prop": {None, "prop-attr", "cond", "data"},
    "cond": {None, "cond-attr", "data"},
    "foreign-key": {None},
    "data": {None},
    "quan": {None},
}

# allowed type, defined in controlled vocabulary
allowed_type = {
    "data": "data-type",
    "file": "file-type",
}

# allowed keyword, defined in controlled vocabulary
allowed_keyword = {
    "process": "process-keyword",
    "process ingredient": "ingredient-keyword",
}
