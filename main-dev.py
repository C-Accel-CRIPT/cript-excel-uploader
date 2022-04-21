import time
import config
from getpass import getpass

import ascii_art
import configs
import sheets
import transformers
import uploaders
import validators

from errors import GroupRelatedError

print(ascii_art.title.template)

token = config.TOKEN
db = uploaders.connect(token)
group_name = config.GROUP
collection_name = config.COLLECTION
path = config.EXCEL_TEMPLATE_FILE_PATH  # input("\nExcel file path: ")

public_flag = None
while public_flag != "y" and public_flag != "n":
    public_flag = input("\nDo you want your data to go public? y/n ---")
public_flag = public_flag == "y"

# Display chem art
print(ascii_art.chem.template)
time.sleep(1)

# Get parameters
param = db.keys

# Instantiate Sheet objects
experiment_sheet = sheets.ExperimentSheet(path, "experiment", param)
data_sheet = sheets.DataSheet(path, "data", param)
file_sheet = sheets.FileSheet(path, "file", param)
material_sheet = sheets.MaterialSheet(path, "material", param)
mixtureComponent_sheet = sheets.MixtureComponentSheet(path, "mixture component", param)
process_sheet = sheets.ProcessSheet(path, "process", param)
#! prerequist
dependentProcess_sheet = sheets.DependentProcessSheet(path, "dependent process", param)
processIngredient_sheet = sheets.ProcessIngredientSheet(
    path, "process ingredient", param
)
processProduct_sheet = sheets.ProcessProductSheet(path, "process product", param)

sheet_dict = {
    "experiment": experiment_sheet,
    "data": data_sheet,
    "file": file_sheet,
    "material": material_sheet,
    "mixture component": mixtureComponent_sheet,
    "process": process_sheet,
    "dependent process": dependentProcess_sheet,
    "process ingredient": processIngredient_sheet,
    "process product": processProduct_sheet,
}
# Check for reading data template

# Validate unique key and not null value
for sheet in sheet_dict.values():
    validators.validate_required_cols(sheet)
    validators.validate_either_or_cols(sheet)
    validators.validate_unique_key(sheet)
    validators.validate_not_null_value(sheet)
    # validators.validate_unit(sheet) # to do
    # validators.validate_keywords(sheet) # to do

# Validate foreign key
for pair in configs.foreign_key_validation_pairs:
    pair["from_sheet_obj"] = sheet_dict[pair["from_sheet_obj"]]
    pair["to_sheet_obj"] = sheet_dict[pair["to_sheet_obj"]]
    validators.validate_foreign_key(**pair)

for sheet in sheet_dict.values():
    for col in sheet.col_parsed:
        parsed_col_name_obj = sheet.col_parsed[col]
        field_list = parsed_col_name_obj.field_list
        if len(field_list) >= 2 and "data" in field_list:
            validators.validate_foreign_key(col, sheet.sheet_name, "name", data_sheet)

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

mixtureComponent_sheet.parse()
print(mixtureComponent_sheet.parsed)
print(f"***********************")

process_sheet.parse()
print(process_sheet.parsed)
print(f"***********************")

processIngredient_sheet.parse()
print(processIngredient_sheet.parsed)
print(f"***********************")

processProduct_sheet.parse()
print(processProduct_sheet.parsed)
print(f"***********************")


bug_count = 0
for sheet in sheet_dict.values():
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

if bug_count != 0:
    exit()

# Transform and Upload parsed data
group_obj = uploaders.get_group(db, group_name)
print(f"group_obj:{group_obj}\n***********************")
collection_obj = uploaders.get_collection(db, group_obj, collection_name)
print(f"coll_obj:{collection_obj}\n***********************")
experiment_objs = transformers.transform_experiment(
    group_obj,
    collection_obj,
    experiment_sheet.parsed,
    public_flag,
)
uploaders.upload(db, experiment_objs)
print(f"expt_objs:{experiment_objs}\n***********************")

data_objs = transformers.transform_data(
    group_obj,
    experiment_objs,
    data_sheet.parsed,
    public_flag,
)
uploaders.upload(db, data_objs)
print(f"data_objs:{data_objs}\n***********************")

file_objs = transformers.transform_file(
    group_obj,
    data_objs,
    file_sheet.parsed,
    public_flag,
)
print(f"file_objs:{file_objs}\n***********************")
# material_objs = transformers.transform_material(
#     group_obj,
#     data_objs,
#     material_sheet.parsed,
#     public_flag,
# )
# uploaders.upload(db, material_objs)
# transformers.transform_components(
#     material_objs,
#     mixtureComponent_sheet.parsed,
# )
# uploaders.upload(db, material_objs)
# print(f"material_objs:{material_objs}\n***********************")
#
# process_objs = transformers.transform_process(
#     group_obj,
#     experiment_objs,
#     process_sheet.parsed,
#     public_flag,
# )
# uploaders.upload(db, process_objs)
# transformers.transform_prerequisite_process(
#     process_objs,
#     dependentProcess_sheet.parsed,
# )
# uploaders.upload(db, process_objs)
# print(f"process_objs:{process_objs}\n***********************")
#
# transformers.transform_process_ingredient(
#     process_objs,
#     material_objs,
#     processIngredient_sheet.parsed,
# )
# uploaders.upload(db, process_objs)
# print(f"process_objs after adding ingredients:{process_objs}\n***********************")
# transformers.transform_process_product(
#     process_objs,
#     material_objs,
#     processProduct_sheet.parsed,
# )
# uploaders.upload(db, process_objs)
# print(f"process_objs after adding products:{process_objs}\n***********************")

# End
print("\n\nAll data was uploaded successfully!\n")
# time.sleep(5)
