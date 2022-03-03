import os
import time

from getpass import getpass

import ascii_art
import sheets
import uploaders

# Display title
from cript.errors import APIAuthError
from errors import GroupRelatedError

print(ascii_art.title.template)

token = None
db = None
while token is None:
    token = input("\nAPI token: ")
    try:
        db = uploaders.connect(token)
    except APIAuthError as e:
        print(f"{e}")
        token = None

# Get Group and Collection names
group = None
while group is None:
    group = input("CRIPT Group (must be an existing group): ")
    try:
        uploaders.upload_group(
            db,
            group,
        )
    except GroupRelatedError as e:
        print(f"{e}\n")
        group = None

collection = input("\nCRIPT Collection: ")

# Get Excel file path
path = input("\nExcel file path: ")
"""To do: file type validation"""
while not os.path.exists(path):
    print("Couldn't find the file. Try again.\n")
    path = input("Excel file path: ")


public_flag = None
while public_flag != "y" and public_flag != "n":
    public_flag = input("\nDo you want your data to go public? y/n ---")
public_flag = public_flag == "y"

# Display chem art
print(ascii_art.chem.template)
time.sleep(1)

# Instantiate Sheet objects
#
material_sheet = sheets.MaterialSheet(path, "material")
experiment_sheet = sheets.ExperimentSheet(path, "experiment")
process_sheet = sheets.ProcessSheet(path, "process")
step_sheet = sheets.StepSheet(path, "step")
stepIngredients_sheet = sheets.StepIngredientSheet(path, "step_ingredients")
stepProducts_sheet = sheets.StepProductSheet(path, "step_products")
data_sheet = sheets.DataSheet(path, "data")
file_sheet = sheets.FileSheet(path, "file")

# Parse Excel sheets
experiment_sheet.parse()
# print(experiment_sheet.parsed)
data_sheet.parse(experiment_sheet.parsed)
# print(data_sheet.parsed)
file_sheet.parse(data_sheet.parsed)
# print(file_sheet.parsed)
material_sheet.parse(data_sheet.parsed)
# print(material_sheet.parsed)
process_sheet.parse(experiment_sheet.parsed)
# print(process_sheet.parsed)
step_sheet.parse(data_sheet.parsed, process_sheet.parsed)
# print(step_sheet.parsed)
stepIngredients_sheet.parse(
    material_sheet.parsed, process_sheet.parsed, step_sheet.parsed
)
# print(stepIngredients_sheet.parsed)
stepProducts_sheet.parse(material_sheet.parsed, process_sheet.parsed, step_sheet.parsed)


# Upload parsed data
print(f"***********************")
group_obj = uploaders.upload_group(
    db,
    group,
)
print(f"group_obj:{group_obj}\n***********************")
coll_obj = uploaders.upload_collection(
    db,
    group_obj,
    collection,
    public_flag,
)
print(f"coll_obj:{coll_obj}\n***********************")
expt_objs = uploaders.upload_experiment(
    db,
    group_obj,
    coll_obj,
    experiment_sheet.parsed,
    public_flag,
)
print(f"expt_objs:{expt_objs}\n***********************")
data_objs = uploaders.upload_data(
    db,
    group_obj,
    expt_objs,
    data_sheet.parsed,
    public_flag,
)
print(f"data_objs:{data_objs}\n***********************")
file_objs = uploaders.upload_file(
    db,
    group_obj,
    data_objs,
    file_sheet.parsed,
    public_flag,
)
print(f"file_objs:{file_objs}\n***********************")
material_objs = uploaders.upload_material(
    db,
    group_obj,
    data_objs,
    material_sheet.parsed,
    public_flag,
)
print(f"material_objs:{material_objs}\n***********************")
process_objs = uploaders.upload_process(
    db,
    group_obj,
    expt_objs,
    process_sheet.parsed,
    public_flag,
)
print(f"process_objs:{process_objs}\n***********************")
step_objs = uploaders.upload_step(
    db,
    group_obj,
    process_objs,
    data_objs,
    step_sheet.parsed,
    public_flag,
)
print(f"step_objs:{step_objs}\n***********************")
uploaders.upload_stepIngredient(
    db,
    process_objs,
    step_objs,
    material_objs,
    stepIngredients_sheet.parsed,
)
print(f"step_objs after adding ingredients:{step_objs}\n***********************")
uploaders.upload_stepProduct(
    db,
    process_objs,
    step_objs,
    material_objs,
    stepProducts_sheet.parsed,
)
print(f"step_objs after adding products:{step_objs}\n***********************")

# End
print("\n\nAll data was uploaded successfully!\n")
# time.sleep(5)
