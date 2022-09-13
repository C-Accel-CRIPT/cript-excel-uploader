import os
import sys
import time
import warnings
from getpass import getpass

import cript
import yaml
import requests

import ascii_art
import parse
import create
from create import error_list
import upload


###
# Setup
###


# Suppress warnings
warnings.filterwarnings("ignore")


# Display title
print(ascii_art.title.template)
time.sleep(1)


# Load config file
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {}


# Establish API connection
connected = False
while connected == False:
    try:
        api = cript.API(
            config.get("host"), config.get("token"), tls=config.get("tls", True)
        )
        connected = True
    except (cript.exceptions.APIAuthError, requests.exceptions.RequestException) as e:
        print(f"~ API connection failed. Try again.\n")
        config["host"] = input("Host (e.g., criptapp.org): ")
        config["token"] = getpass("API Token: ")


# Get Excel file path
while config.get("path") is None or not os.path.exists(config.get("path")):
    print("~ Could not find the file. Try again.\n")
    config["path"] = input("Path to Excel file: ").strip('"')


# Get Project
project = None
while project is None:
    try:
        project = api.get(cript.Project, {"name": config.get("project")})
    except cript.exceptions.APIGetError:
        print("~ Could not find the specified project. Try again.\n")
        config["project"] = input("Project name: ")


# Get Collection
collection = None
while collection is None:
    try:
        collection = api.get(
            cript.Collection,
            {"name": config.get("collection"), "project": project.uid},
        )
    except cript.exceptions.APIGetError:
        print("~ Could not find the specified collection. Try again.\n")
        config["collection"] = input("Collection name: ")


# Get privacy settings
public = config.get("public")
while public is None or not isinstance(public, bool):
    public = input("Do you want your data visible to the public? (yes/no): ")
    public = public.lower() == "yes"


# Display chem art
print(ascii_art.chem.template)


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


###
# Parse
###


parsed_sheets = {}
for parameter in sheet_parameters:
    # Creates a Sheet object to be parsed for each sheet
    parsed_sheets[parameter["name"]] = parse.Sheet(
        config["path"],
        parameter["name"],
        parameter["required_columns"],
        unique_columns=parameter["unique_columns"],
    ).parse()


###
# Create and validate
###

experiments = create.create_experiments(parsed_sheets["experiment"], collection, public)
references, citations = create.create_citations(
    parsed_sheets["citation"], project.group, public
)
data, files = create.create_data(
    parsed_sheets["data"], project, experiments, citations, public
)
materials = create.create_materials(
    parsed_sheets["material"], project, data, citations, public
)
materials = create.create_mixtures(parsed_sheets["mixture component"], materials)
processes = create.create_processes(
    parsed_sheets["process"], experiments, data, citations, public
)
create.create_prerequisites(parsed_sheets["prerequisite process"], processes)
create.create_ingredients(parsed_sheets["process ingredient"], processes, materials)
create.create_products(parsed_sheets["process product"], processes, materials)
create.create_equipment(parsed_sheets["process equipment"], processes, data, citations)


# Print errors
if error_list:
    print("-- ERRORS --\n")
    for error in error_list:
        print(f"{error}\n")
    sys.exit(1)


###
# Upload
###


upload.upload(api, experiments, "Experiment")
upload.upload(api, references, "Reference")
upload.upload(api, data, "Data")
upload.upload(api, materials, "Material")
upload.upload(api, processes, "Process")
upload.upload(api, files, "File")
upload.add_sample_preparation_to_process(parsed_sheets["data"], data, processes, api)

###
# Finish
###


# Print message
collection_url = collection.url.replace("api/", "")
print(f"\n\nThe upload was successful!")
print(f"You can view your collection here: {collection_url}\n\n")
input("Press ENTER to exit.")
