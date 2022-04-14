import cript as C
import inspect

required_cols = {
    "experiment": ["name"],
    "data": ["experiment", "name", "type"],
    "file": ["data", "source", "type"],
    "material": ["name"],
    "mixture components": ["material", "component"],
    "process": ["experiment", "name", "keywords"],
    "dependent processes": ["process", "dependent_process"],
    "process ingredients": ["process", "material", "keyword"],
    "process products": ["process", "product"],
}

either_or_cols = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": [],
    "mixture components": [],
    "process": [],
    "dependent processes": [],
    "step": [],
    "process ingredients": ["mole", "mass", "volume"],
    "process products": [],
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
    "mixture components": ["material+component"],
    "process": ["name"],
    "dependent processes": ["process+dependent_process"],
    "process ingredients": ["process+material"],
    "process products": ["process+product"],
}

foreign_keys = {
    "experiment": [],
    "data": ["experiment"],
    "file": ["data"],
    "material": [],
    "mixture components": ["material", "component"],
    "process": ["experiment"],
    "dependent processes": ["process", "dependent_process"],
    "process ingredients": ["process", "ingredient"],
    "process products": ["process", "product"],
}

list_fields = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": ["names"],
    "mixture components": [],
    "process": ["keywords"],
    "dependent processes": [],
    "process ingredients": [],
    "process products": [],
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
    "mixture components": {},
    "process": {"process"},
    "dependent processes": {},
    "process ingredients": {"ingredient"},
    "process products": {},
}

sheet_name_to_prop_key = {
    "material": "material-property-key",
    "process": "process-property-key",
}

foreign_key_validation_pairs = [
    {
        "from_field": "experiment",
        "from_sheet_obj": "data_sheet",
        "to_field": "name",
        "to_sheet_obj": "experiment_sheet",
    },
    {
        "from_field": "data",
        "from_sheet_obj": "file_sheet",
        "to_field": "name",
        "to_sheet_obj": "data_sheet",
    },
    {
        "from_field": "experiment",
        "from_sheet_obj": "process_sheet",
        "to_field": "name",
        "to_sheet_obj": "experiment_sheet",
    },
    {
        "from_field": "process",
        "from_sheet_obj": "processIngredients_sheet",
        "to_field": "name",
        "to_sheet_obj": "process_sheet",
    },
    {
        "from_field": "process",
        "from_sheet_obj": "dependentProcess_sheet",
        "to_field": "name",
        "to_sheet_obj": "process_sheet",
    },
    {
        "from_field": "dependent_process",
        "from_sheet_obj": "dependentProcess_sheet",
        "to_field": "name",
        "to_sheet_obj": "process_sheet",
    },
    {
        "from_field": "material",
        "from_sheet_obj": "stepIngredients_sheet",
        "to_field": "name",
        "to_sheet_obj": "material_sheet",
    },
    {
        "from_field": "product",
        "from_sheet_obj": "stepProducts_sheet",
        "to_field": "name",
        "to_sheet_obj": "material_sheet",
    },
    {
        "from_field": "material",
        "from_sheet_obj": "mixtureComponent_sheet",
        "to_field": "name",
        "to_sheet_obj": "material_sheet",
    },
    {
        "from_field": "component",
        "from_sheet_obj": "mixtureComponent_sheet",
        "to_field": "name",
        "to_sheet_obj": "material_sheet",
    },
]
