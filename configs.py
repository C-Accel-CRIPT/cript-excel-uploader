import cript as C
import inspect
from util import filter_required_col

required_cols = {
    "experiment": filter_required_col(C.Experiment.required),
    "data": filter_required_col(C.Data.required),
    "file": filter_required_col(C.File.required),
    "material": filter_required_col(C.Material.required),
    "mixture component": ["material", "component"],
    "process": filter_required_col(C.Process.required),
    "dependent process": ["process", "dependent_process"],
    "process ingredient": ["process", "ingredient", "keyword"],
    "process product": ["process", "product"],
}

either_or_cols = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": [],
    "mixture component": [],
    "process": [],
    "dependent process": [],
    "step": [],
    "process ingredient": ["mole", "mass", "volume"],
    "process product": [],
}

unique_keys = {
    "experiment": ["name"],
    "data": ["name"],
    "file": [],
    "material": ["name"],
    "mixture component": ["material+component"],
    "process": ["name"],
    "dependent process": ["process+dependent_process"],
    "process ingredient": ["process+material"],
    "process product": ["process+product"],
}

foreign_keys = {
    "experiment": [],
    "data": ["experiment"],
    "file": ["data"],
    "material": [],
    "mixture component": ["material", "component"],
    "process": ["experiment"],
    "dependent process": ["process", "dependent_process"],
    "process ingredient": ["process", "ingredient"],
    "process product": ["process", "product"],
}

list_fields = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": ["names"],
    "mixture component": [],
    "process": ["keywords"],
    "dependent process": [],
    "process ingredient": [],
    "process product": [],
}


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

# sheet_nodes
base_nodes = {
    "experiment": {"experiment"},
    "data": {"data"},
    "file": {"file"},
    "material": {"material"},
    "mixture component": {},
    "process": {"process"},
    "dependent process": {},
    "process ingredient": {"ingredient"},
    "process product": {},
}

sheet_name_to_prop_key = {
    "material": "material-property-key",
    "process": "process-property-key",
}

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
        "from_sheet_obj": "dependent process",
        "to_field": "name",
        "to_sheet_obj": "process",
    },
    {
        "from_field": "dependent_process",
        "from_sheet_obj": "dependent process",
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

allowed_data_assignment = {
    "base": {None, "prop", "cond", "data"},
    "prop": {None, "prop-attr", "cond", "data"},
    "cond": {None, "cond-attr", "data"},
    "foreign-key": {None},
    "data": {None},
    "quan": {None},
}
