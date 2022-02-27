import os
import time

from getpass import getpass

import ascii_art
import sheets
import uploaders

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

path = r"C:\Users\Orange Meow\Desktop\MIT CRIPT\excel_uploader\excel template\example_template_NEW_0226.xlsx"
"""To do: file type validation"""
while not os.path.exists(path):
    print("\nCouldn't find the file. Try again.\n")
    path = input("Excel file path: ")

# Get Group and Collection names
# group = input("\nCRIPT Group (must be an existing group): ")
# collection = input("\nCRIPT Collection: ")
group = "Olsen_Lab"
collection = "test0226"

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
print(experiment_sheet.parsed)
data_sheet.parse(experiment_sheet.parsed)
print(data_sheet.parsed)
file_sheet.parse(data_sheet.parsed)
print(file_sheet.parsed)
material_sheet.parse(data_sheet.parsed)
print(material_sheet.parsed)
process_sheet.parse(experiment_sheet.parsed)
print(process_sheet.parsed)
step_sheet.parse(data_sheet.parsed, process_sheet.parsed)
print(step_sheet.parsed)
stepIngredients_sheet.parse(
    material_sheet.parsed, process_sheet.parsed, step_sheet.parsed
)
print(stepIngredients_sheet.parsed)
stepProducts_sheet.parse(material_sheet.parsed, process_sheet.parsed, step_sheet.parsed)


# Upload parsed data
# group_uid = uploaders.upload_group(db, group)
# coll_uid = uploaders.upload_collection(db, group_uid, collection)
# expt_uids = uploaders.upload_experiment(db, coll_uid, experiment_sheet.parsed)
# data_uids = uploaders.upload_data(db, expt_uids, data_sheet.parsed)
# reagent_uids = uploaders.upload_material(db, reagent_sheet.parsed, data_uids, "reagent")
# process_uids = uploaders.upload_process(
#     db, expt_uids, ingr_sheet.parsed, process_sheet.parsed, reagent_uids, data_uids
# )
# product_uids = uploaders.upload_material(
#     db, product_sheet.parsed, data_uids, "product", process_uids
# )


# db = uploaders.connect()
# group_url = uploaders.upload_group(db, group)
# coll_url = uploaders.upload_collection(db, group_url, collection)
# expt_urls = uploaders.upload_experiment(db, group_url, coll_url, experiment_sheet.parsed)
# data_urls = uploaders.upload_data(db,group_url,expt_urls,data_sheet.parsed)


# End
print("\n\nAll data was uploaded successfully!\n")
# time.sleep(5)
