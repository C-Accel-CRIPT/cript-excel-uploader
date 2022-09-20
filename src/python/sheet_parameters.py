# Define sheet parameters
sheet_parameters = [
    {
        "name": "experiment",
        "required_columns": ("name",),
        "unique_columns": ("name",),
    },
    {
        "name": "citation",
        "required_columns": ("title",),
        "unique_columns": ("title",),
    },
    {
        "name": "data",
        "required_columns": ("experiment", "name", "type", "path"),
        "unique_columns": ("name",),
    },
    {
        "name": "material",
        "required_columns": ("name",),
        "unique_columns": ("name",),
    },
    {
        "name": "mixture component",
        "required_columns": ("mixture", "material"),
        "unique_columns": ("mixture", "material"),
    },
    {
        "name": "process",
        "required_columns": ("experiment", "name", "type"),
        "unique_columns": ("name",),
    },
    {
        "name": "prerequisite process",
        "required_columns": ("process", "prerequisite"),
        "unique_columns": ("process", "prerequisite"),
    },
    {
        "name": "process ingredient",
        "required_columns": ("process", "materials", "keyword"),
        "unique_columns": ("process", "material", "keyword"),
    },
    {
        "name": "process product",
        "required_columns": ("process", "material"),
        "unique_columns": ("process", "material"),
    },
    {
        "name": "process equipment",
        "required_columns": ("process", "key"),
        "unique_columns": ("process", "key"),
    },
]
