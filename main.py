import os
import sys
import time
import warnings
from getpass import getpass
from pprint import pprint

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
        api = cript.API(config.get("host"), config.get("token"))
        connected = True
    except (cript.exceptions.APIAuthError, requests.exceptions.RequestException) as e:
        print(f"~ API connection failed. Try again.\n")
        config["host"] = input("Host (e.g., criptapp.org): ")
        config["token"] = getpass("API Token: ")


# Get Excel file path
while not os.path.exists(config.get("path")):
    print("~ Could not find the file. Try again.\n")
    config["path"] = input("Path to Excel file: ").strip('"')


# Get Group
group = None
while group is None:
    try:
        group = api.get(
            cript.Group, {"name": config.get("group"), "created_by": api.user.uid}
        )
    except cript.exceptions.APIGetError:
        print("~ Could not find the specified group. Try again.\n")
        config["group"] = input("Group name: ")


# Get Collection
collection = None
while collection is None:
    try:
        collection = api.get(
            cript.Collection,
            {"name": config.get("collection"), "created_by": api.user.uid},
        )
    except cript.exceptions.APIGetError:
        print("~ Could not find the specified collection. Try again.\n")
        config["collection"] = input("Collection name: ")


# Prompt user for privacy setting
public = input("Do you want your data visible to the public? (y/N): ").lower() == "y"


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
        "required_columns": ("experiment", "name"),
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

experiments = create.create_experiments(
    parsed_sheets["experiment"], group, collection, public
)
references, citations = create.create_citations(
    parsed_sheets["citation"], group, public
)
data, files = create.create_data(
    parsed_sheets["data"], group, experiments, citations, public
)
materials = create.create_materials(
    parsed_sheets["material"], group, data, citations, public
)
materials = create.create_mixtures(parsed_sheets["mixture component"], materials)
processes = create.create_processes(
    parsed_sheets["process"], group, experiments, data, citations, public
)
create.create_ingredients(parsed_sheets["process ingredient"], processes, materials)
create.create_products(parsed_sheets["process product"], processes, materials)
create.create_prerequisites(parsed_sheets["prerequisite process"], processes)


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


###
# Finish
###


# Print message
print("\n\nAll data was uploaded successfully.\n")
time.sleep(5)
