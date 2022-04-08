import cript as C
import inspect

required_cols = {
    "experiment": ["name"],
    "data": ["experiment", "name", "type"],
    "file": ["data", "source", "type"],
    "material": ["name"],
    "process": ["experiment", "name"],
    "step": ["process", "step_id", "type"],
    "step_ingredients": ["process", "step_id", "keyword", "ingredient"],
    "step_products": ["process", "step_id", "product"],
}

either_or_cols = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": [],
    "process": [],
    "step": [],
    "step_ingredients": ["mole", "mass", "volume"],
    "step_products": [],
}

integer_cols = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": [],
    "process": [],
    "step": ["step_id"],
    "step_ingredients": ["step_id"],
    "step_products": ["step_id"],
}

float_cols = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": ["molar_mass", "temp_boil", "temp_melt"],
    "process": [],
    "step": [],
    "step_ingredients": ["mole", "mass", "volume"],
    "step_products": [],
}

unique_keys = {
    "experiment": ["name"],
    "data": ["name"],
    "file": ["path"],
    "material": ["name"],
    "process": ["name"],
    "step": ["process:step_id"],
    "step_ingredients": ["process:step_id:ingredient"],
    "step_products": ["process:step_id:product"],
}

foreign_keys = {
    "experiment": [],
    "data": ["experiment"],
    "file": ["data"],
    "material": [],
    "process": ["experiment"],
    "step": ["process"],
    "step_ingredients": ["process", "step_id", "ingredient"],
    "step_products": ["process", "step_id", "product"],
}

list_fields = {
    "experiment": [],
    "data": [],
    "file": [],
    "material": ["keywords", "names"],
    "process": ["keywords"],
    "step": ["equipment"],
    "step_ingredients": [],
    "step_products": [],
}

base_cols = {}
base_cols["experiment"] = inspect.signature(C.Experiment.__init__).parameters
base_cols["material"] = inspect.signature(C.Material.__init__).parameters
base_cols["data"] = inspect.signature(C.Data.__init__).parameters
base_cols["file"] = inspect.signature(C.File.__init__).parameters
base_cols["process"] = inspect.signature(C.Process.__init__).parameters

# sheet_nodes
base_nodes = {
    "experiment": {"experiment"},
    "data": {"data", "file"},
    "material": {"material"},
    "process": {"process"},
    "step": {"step"},
    "step_ingredients": {"materialIngredient"},
    "step_products": {},
}

sheet_name_to_prop_key = {
    "material": "material-property-key",
    "step": "step-property-key",
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
        "from_sheet_obj": "step_sheet",
        "to_field": "name",
        "to_sheet_obj": "process_sheet",
    },
    {
        "from_field": "process",
        "from_sheet_obj": "stepIngredients_sheet",
        "to_field": "name",
        "to_sheet_obj": "process_sheet",
    },
    {
        "from_field": "process",
        "from_sheet_obj": "stepProducts_sheet",
        "to_field": "name",
        "to_sheet_obj": "process_sheet",
    },
    {
        "from_field": "process:step_id",
        "from_sheet_obj": "stepIngredients_sheet",
        "to_field": "process:step_id",
        "to_sheet_obj": "step_sheet",
    },
    {
        "from_field": "process:step_id",
        "from_sheet_obj": "stepProducts_sheet",
        "to_field": "process:step_id",
        "to_sheet_obj": "step_sheet",
    },
    {
        "from_field": "ingredient-material",
        "from_sheet_obj": "stepIngredients_sheet",
        "to_field": "name",
        "to_sheet_obj": "material_sheet",
    },
    {
        "from_field": "ingredient-step",
        "from_sheet_obj": "stepIngredients_sheet",
        "to_field": "process:step_id",
        "to_sheet_obj": "step_sheet",
    },
    {
        "from_field": "product",
        "from_sheet_obj": "stepProducts_sheet",
        "to_field": "material",
        "to_sheet_obj": "material_sheet",
    },
]
