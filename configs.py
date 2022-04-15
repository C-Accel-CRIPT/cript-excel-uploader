import cript as C
import inspect

required_cols = {
    "experiment": ["name"],
    "data": ["experiment", "name", "type"],
    "file": ["data", "source", "type"],
    "material": ["name"],
    "mixture component": ["material", "component"],
    "process": ["experiment", "name", "keywords"],
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

# integer_cols = {
#     "experiment": [],
#     "data": [],
#     "file": [],
#     "material": [],
#     "process": [],
#     "step": ["step_id"],
#     "step_ingredients": ["step_id"],
#     "step_products": ["step_id"],
# }
#
# float_cols = {
#     "experiment": [],
#     "data": [],
#     "file": [],
#     "material": ["molar_mass", "temp_boil", "temp_melt"],
#     "process": [],
#     "step": [],
#     "step_ingredients": ["mole", "mass", "volume"],
#     "step_products": [],
# }

unique_keys = {
    "experiment": ["name"],
    "data": ["name"],
    "file": ["source"],
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

base_cols = {}
base_cols["experiment"] = inspect.signature(C.Experiment.__init__).parameters
base_cols["material"] = inspect.signature(C.Material.__init__).parameters
base_cols["data"] = inspect.signature(C.Data.__init__).parameters
base_cols["file"] = inspect.signature(C.File.__init__).parameters
base_cols["process"] = inspect.signature(C.Process.__init__).parameters
base_cols["ingredient"] = inspect.signature(C.Ingredient.__init__).parameters


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
