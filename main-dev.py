import os
import time
import config
from getpass import getpass

import ascii_art
import sheets
import uploaders
import validators

# Display title
from cript.errors import APIAuthError
from errors import GroupRelatedError

print(ascii_art.title.template)

token = None
db = None
while token is None:
    token = config.TOKEN  # input("\nAPI token: ")
    try:
        db = uploaders.connect(token)
    except APIAuthError as e:
        print(f"{e}")
        token = None

# Get Group and Collection names
group = config.GROUP
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

collection = config.COLLECTION  # input("\nCRIPT Collection: ")

# Get Excel file path
path = config.EXCEL_TEMPLATE_FILE_PATE  # input("\nExcel file path: ")
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

# Get parameters
param = db.get_keys()

# Instantiate Sheet objects
material_sheet = sheets.MaterialSheet(path, "material", param)
experiment_sheet = sheets.ExperimentSheet(path, "experiment", param)
process_sheet = sheets.ProcessSheet(path, "process", param)
step_sheet = sheets.StepSheet(path, "step", param)
stepIngredients_sheet = sheets.StepIngredientSheet(path, "step_ingredients", param)
stepProducts_sheet = sheets.StepProductSheet(path, "step_products", param)
data_sheet = sheets.DataSheet(path, "data", param)
file_sheet = sheets.FileSheet(path, "file", param)

sheet_list = [
    material_sheet,
    experiment_sheet,
    process_sheet,
    step_sheet,
    stepIngredients_sheet,
    stepProducts_sheet,
    data_sheet,
    file_sheet,
]
# Check for reading data template

# Validate unique key and not null value
for sheet in sheet_list:
    validators.validate_required_cols(sheet)
    validators.validate_either_or_cols(sheet)
    validators.validate_unique_key(sheet)
    validators.validate_not_null_value(sheet)
    # validators.validate_unit(sheet) # to be discussed

# Validate foreign key
validators.validate_foreign_key("experiment", data_sheet, "name", experiment_sheet)
validators.validate_foreign_key("data", file_sheet, "name", data_sheet)
validators.validate_foreign_key("experiment", process_sheet, "name", experiment_sheet)
validators.validate_foreign_key("process", step_sheet, "name", process_sheet)
validators.validate_foreign_key("process", stepIngredients_sheet, "name", process_sheet)
validators.validate_foreign_key(
    "process:step_id", stepIngredients_sheet, "process:step_id", step_sheet
)
validators.validate_foreign_key(
    "process:step_id", stepProducts_sheet, "process:step_id", step_sheet
)
validators.validate_foreign_key(
    "ingredient-material", stepIngredients_sheet, "name", material_sheet
)
validators.validate_foreign_key(
    "ingredient-step", stepIngredients_sheet, "process+step_id", step_sheet
)
validators.validate_foreign_key("product", stepProducts_sheet, "name", material_sheet)
for sheet in sheet_list:
    for field in sheet.col_lists_dict:
        col_list = sheet.col_lists_dict[field]
        if len(col_list) == 2 and col_list[-1] == "data":
            validators.validate_foreign_key(field, sheet.sheet_name, "name", data_sheet)

# Parse Excel sheets
print(f"***********************")
experiment_sheet.parse()
print(experiment_sheet.parsed)
print(f"***********************")
data_sheet.parse()
print(data_sheet.parsed)
print(f"***********************")
file_sheet.parse()
print(file_sheet.parsed)
print(f"***********************")
material_sheet.parse()
print(material_sheet.parsed)
print(f"***********************")
process_sheet.parse()
print(process_sheet.parsed)
print(f"***********************")
step_sheet.parse()
print(step_sheet.parsed)
print(f"***********************")
stepIngredients_sheet.parse()
print(stepIngredients_sheet.parsed)
print(f"***********************")
stepProducts_sheet.parse()
print(stepProducts_sheet.parsed)

print(f"***********************")
bug_count = 0
for sheet in sheet_list:
    for exception_message in sheet.errors:
        print(exception_message)
        bug_count = bug_count + 1
        if bug_count >= 500:
            break
    if bug_count >= 500:
        break

if bug_count == 0:
    print(f"No bugs here! Your excel sheet looks good. Start uploading now.")
elif bug_count < 500:
    print(f"\nYou have {bug_count} bugs to fix.")
elif bug_count >= 500:
    print(
        f"\nYou have too many bugs. "
        f"Fix the 500 bugs above first and have a check again."
    )
print(f"***********************")

# # Upload parsed data
# print(f"***********************")
# group_obj = uploaders.upload_group(
#     db,
#     group,
# )
# #print(f"group_obj:{group_obj}\n***********************")
# coll_obj = uploaders.upload_collection(
#     db,
#     group_obj,
#     collection,
#     public_flag,
# )
# #print(f"coll_obj:{coll_obj}\n***********************")
# expt_objs = uploaders.upload_experiment(
#     db,
#     group_obj,
#     coll_obj,
#     experiment_sheet.parsed,
#     public_flag,
# )
# #print(f"expt_objs:{expt_objs}\n***********************")
# data_objs = uploaders.upload_data(
#     db,
#     group_obj,
#     expt_objs,
#     data_sheet.parsed,
#     public_flag,
# )
# #print(f"data_objs:{data_objs}\n***********************")
# file_objs = uploaders.upload_file(
#     db,
#     group_obj,
#     data_objs,
#     file_sheet.parsed,
#     public_flag,
# )
# #print(f"file_objs:{file_objs}\n***********************")
# material_objs = uploaders.upload_material(
#     db,
#     group_obj,
#     data_objs,
#     material_sheet.parsed,
#     public_flag,
# )
# #print(f"material_objs:{material_objs}\n***********************")
# process_objs = uploaders.upload_process(
#     db,
#     group_obj,
#     expt_objs,
#     process_sheet.parsed,
#     public_flag,
# )
# #print(f"process_objs:{process_objs}\n***********************")
# step_objs = uploaders.upload_step(
#     db,
#     group_obj,
#     process_objs,
#     data_objs,
#     step_sheet.parsed,
#     public_flag,
# )
# #print(f"step_objs:{step_objs}\n***********************")
# uploaders.upload_stepIngredient(
#     db,
#     process_objs,
#     step_objs,
#     material_objs,
#     stepIngredients_sheet.parsed,
# )
# #print(f"step_objs after adding ingredients:{step_objs}\n***********************")
# uploaders.upload_stepProduct(
#     db,
#     process_objs,
#     step_objs,
#     material_objs,
#     stepProducts_sheet.parsed,
# )
# #print(f"step_objs after adding products:{step_objs}\n***********************")

# End
print("\n\nAll data was uploaded successfully!\n")
# time.sleep(5)
