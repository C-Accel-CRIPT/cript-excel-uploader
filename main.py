import os
import time

from getpass import getpass

import ascii_art
import sheets
import uploaders


# Display title
print(ascii_art.title.template)


# Get DB info
db_project = input("DB Project: ")
db_database = input("DB Name: ")
db_username = input("DB Username: ")
db_password = getpass("DB Password: ")


# Get User email and establish connection to CRIPT database
user = input("\nCRIPT User email: ")
db = uploaders.connect(db_username, db_password, db_project, db_database, user)


# Get Excel file path
path = input("\nExcel file path: ")
while not os.path.exists(path):
    print("\nCouldn't find the file. Try again.\n")
    path = input("Excel file path: ")


# Get Group and Collection names
group = input("\nCRIPT Group (must be an existing group): ")
collection = input("\nCRIPT Collection: ")


# Display chem art
print(ascii_art.chem.template)
time.sleep(1)


# Instantiate Sheet objects
experiment_sheet = sheets.ExperimentSheet(path, 'experiment')
data_sheet = sheets.DataSheet(path, 'data')
reagent_sheet = sheets.MaterialSheet(path, 'reagent_material')
process_sheet = sheets.ProcessSheet(path, 'process')
ingr_sheet = sheets.IngrSheet(path, 'process_ingredients')
product_sheet = sheets.MaterialSheet(path, 'product_material')


# Parse Excel sheets
experiment_sheet.parse()
data_sheet.parse(experiment_sheet.parsed)
reagent_sheet.parse(data_sheet.parsed)
process_sheet.parse(experiment_sheet.parsed, data_sheet.parsed)
ingr_sheet.parse(process_sheet.parsed, reagent_sheet.parsed)
product_sheet.parse(data_sheet.parsed, process_sheet.parsed)


# Upload parsed data
group_uid = uploaders.upload_group(db, group)
coll_uid = uploaders.upload_collection(db, group_uid, collection)
expt_uids = uploaders.upload_experiment(db, coll_uid, experiment_sheet.parsed)
data_uids = uploaders.upload_data(db, expt_uids, data_sheet.parsed)
reagent_uids = uploaders.upload_material(db, reagent_sheet.parsed, data_uids, 'reagent')
process_uids = uploaders.upload_process(db, expt_uids, ingr_sheet.parsed, process_sheet.parsed, reagent_uids, data_uids)
product_uids = uploaders.upload_material(db, product_sheet.parsed, data_uids, 'product', process_uids)


# End
print("\n\nAll data was uploaded successfully!\n")
time.sleep(5)