required_cols = {
    "experiment": ["name"],
    "data": ["experiment", "name", "type"],
    "file": ["data", "source", "type"],
    "material": ["name", "keywords"],
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


base_cols = {
    "experiment": {
        "name",
        "funding",
        "notes",
    },
    "data": {
        "name",
        "type",
        "sample_prep",
        "calibration",
        "configuration",
        "notes",
    },
    "file": {
        "source",
        "type",
        "external_source",
    },
    "identity": {
        "name",
        "names",
        "cas",
        "smiles",
        "bigsmiles",
        "chem_formula",
        "chem_repeat",
        "pubchem_cid",
        "inchi",
        "inchi_key",
    },
    "material": {
        "name",
        "vendor",
        "lot_number",
        "keywords",
        "notes",
    },
    "process": {
        "name",
        "keywords",
        "notes",
    },
    "step": {
        "step_id",
        "type",
        "description",
        "equipment",
    },
    "materialIngredient": {
        "keyword",
        "method",
    },
    "quantity": {
        "key",
        "value",
        "unit",
    },
    "property": {
        "key",
        "value",
        "unit",
        "type",
        "method",
        "method_description",
        "uncertainty",
        "uncertainty_type",
    },
}
# sheet_nodes
base_nodes = {
    "experiment": {"experiment"},
    "data": {"data"},
    "file": {"file"},
    "material": {"material", "identity"},
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
