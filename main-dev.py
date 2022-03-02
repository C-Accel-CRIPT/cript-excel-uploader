import os
import time

from getpass import getpass

import ascii_art
import sheets
import uploaders
import config

# Display title
print(ascii_art.title.template)

# Get DB info
# db_project = input("DB Project: ")
# db_database = input("DB Name: ")
# db_username = input("DB Username: ")
# db_password = getpass("DB Password: ")


# Get User email and establish connection to CRIPT database
# user = input("\nCRIPT User email: ")
# db = uploaders.connect()

# Get Excel file path
# path = input("\nExcel file path: ")

path = config.EXCEL_TEMPLATE_FILE_PATE
"""To do: file type validation"""
while not os.path.exists(path):
    print("\nCouldn't find the file. Try again.\n")
    path = input("Excel file path: ")

# Get Group and Collection names
# group = input("\nCRIPT Group (must be an existing group): ")
# collection = input("\nCRIPT Collection: ")
group = "TestGroup3"
collection = "excel_uploader_test0227_5"

# Display chem art
# print(ascii_art.chem.template)
# time.sleep(1)

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
# print("parsing")
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
db = uploaders.connect()
print(f"***********************")
group_obj = uploaders.upload_group(db, group)
print(f"group_obj:{group_obj}\n***********************")
coll_obj = uploaders.upload_collection(db, group_obj, collection)
print(f"coll_obj:{coll_obj}\n***********************")
expt_objs = uploaders.upload_experiment(
    db, group_obj, coll_obj, experiment_sheet.parsed
)
print(f"expt_objs:{expt_objs}\n***********************")
data_objs = uploaders.upload_data(db, group_obj, expt_objs, data_sheet.parsed)
print(f"data_objs:{data_objs}\n***********************")
# file_objs = uploaders.upload_file(db, group_obj, data_objs, file_sheet.parsed)
# print(f"file_objs:{file_objs}\n***********************")
material_objs = uploaders.upload_material(
    db, group_obj, data_objs, material_sheet.parsed
)
print(f"material_objs:{material_objs}\n***********************")
process_objs = uploaders.upload_process(db, group_obj, expt_objs, process_sheet.parsed)
print(f"process_objs:{process_objs}\n***********************")
print(step_sheet.parsed)
step_objs = uploaders.upload_step(
    db, group_obj, process_objs, data_objs, step_sheet.parsed
)
print(f"step_objs:{step_objs}\n***********************")
print(stepIngredients_sheet.parsed)
stepIngredient_objs = uploaders.upload_stepIngredient(
    db, group_obj, process_objs, step_objs, data_objs, stepIngredients_sheet.parsed
)
print(f"stepIngredient_objs:{stepIngredient_objs}\n***********************")

# db = uploaders.connect()
# group_url = uploaders.upload_group(db, group)
# coll_url = uploaders.upload_collection(db, group_url, collection)
# expt_urls = uploaders.upload_experiment(db, group_url, coll_url, experiment_sheet.parsed)
# data_urls = uploaders.upload_data(db,group_url,expt_urls,data_sheet.parsed)


# End
print("\n\nAll data was uploaded successfully!\n")
# time.sleep(5)
