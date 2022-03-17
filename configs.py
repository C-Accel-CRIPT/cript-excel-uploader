required_cols = {
    "experiment": ["name"],
    "data": ["experiment", "name", "type"],
    "file": ["data", "source"],
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

not_null_cols = {
    "experiment": ["name"],
    "data": ["experiment", "name", "data_type"],
    "file": ["data", "path"],
    "material": ["name"],
    "process": ["experiment", "name"],
    "step": ["process", "step_id", "step_type", "keywords"],
    "step_ingredients": ["process", "step_id", "keyword", "ingredient"],
    "step_products": ["process", "step_id", "keyword", "product"],
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
        "experiment",
        "name",
        "type",
        "sample_prep",
        "calibration",
        "configuration",
        "notes",
    },
    "file": {
        "source",
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
}

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
