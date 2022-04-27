import time
import os

from src import ascii_art
from src import configs
from src import sheets
from src import transformers
from src import uploaders
from src import util
from src import validators

print(ascii_art.title.template)
_config_key_dict, _config_is_found = util.read_config()

base_url = _config_key_dict.get("BASE_URL")
token = _config_key_dict.get("TOKEN")
group_name = _config_key_dict.get("GROUP")
collection_name = _config_key_dict.get("COLLECTION")
path = _config_key_dict.get("EXCEL_TEMPLATE_FILE_PATH")
public_flag = None


# API connection
db = None
while db is None:
    if base_url is None:
        base_url = input("\nBase URL: ")
    if token is None:
        token = input("\nAPI token: ")
    try:
        print("Checking token...")
        db = uploaders.connect(base_url, token)
        print("")
    except Exception as e:
        print(e.__str__())
        token = None


# Group
group_obj = None
while group_obj is None:
    if group_name is None or len(group_name) == 0:
        group_name = input("\nCRIPT Group (must be an existing group): ")
    try:
        print("Checking group...")
        group_obj = uploaders.get_group(
            db,
            group_name,
        )
        print("Valid group.\n")
    except Exception as e:
        print(e.__str__())
        group_name = None


# Collection
collection_obj = None
while collection_obj is None:
    if collection_name is None or len(collection_name) == 0:
        collection_name = input("\nCRIPT Collection (must be an existing collection): ")
    try:
        print("Checking collection...")
        collection_obj = uploaders.get_collection(
            db,
            group_obj,
            collection_name,
        )
        print("Valid collection.\n")
    except Exception as e:
        print(e.__str__())
        collection_name = None


# Excel file path
if _config_is_found:
    print("Checking file path...")
while (
    path is None
    or len(path) == 0
    or not os.path.exists(path)
    or os.path.splitext(path)[-1] != ".xlsx"
):
    if path is None or len(path) == 0:
        pass
    elif not os.path.exists(path):
        print("File not found. Try again.")
    else:
        print("This is not an excel file. Try again.")
    path = input("\nExcel file path: ")
    print("Checking file path...")
print("Excel file found.\n")


# Public flag
while public_flag != "y" and public_flag != "n":
    public_flag = input("\nDo you want your data to go public? y/n ---").lower()
public_flag = public_flag == "y"


# Display chem art
print(ascii_art.chem.template)
time.sleep(1)

# Get parameters and user uid
param = db.keys
user_uid = db.user.uid


# Instantiate Sheet objects
def construct_sheet_objs():
    experiment_sheet = sheets.ExperimentSheet(path, "experiment", param)
    data_sheet = sheets.DataSheet(path, "data", param)
    file_sheet = sheets.FileSheet(path, "file", param)
    material_sheet = sheets.MaterialSheet(path, "material", param)
    mixture_component_sheet = sheets.MixtureComponentSheet(
        path, "mixture component", param
    )
    process_sheet = sheets.ProcessSheet(path, "process", param)
    prerequisite_process_sheet = sheets.PrerequisiteProcessSheet(
        path, "prerequisite process", param
    )
    process_ingredient_sheet = sheets.ProcessIngredientSheet(
        path, "process ingredient", param
    )
    process_product_sheet = sheets.ProcessProductSheet(path, "process product", param)

    _sheet_dict = {
        "experiment": experiment_sheet,
        "data": data_sheet,
        "file": file_sheet,
        "material": material_sheet,
        "mixture component": mixture_component_sheet,
        "process": process_sheet,
        "prerequisite process": prerequisite_process_sheet,
        "process ingredient": process_ingredient_sheet,
        "process product": process_product_sheet,
    }

    return _sheet_dict


# Validate required col, either or col, unique key, not null value, type and keyword
def validate_and_parse_sheets(_sheet_dict):
    for sheet in _sheet_dict.values():
        validators.validate_required_cols(sheet)
        validators.validate_either_or_cols(sheet)
        validators.validate_unique_key(sheet)
        validators.validate_not_null_value(sheet)
        # validators.validate_file_source(sheet)
        validators.validate_type(sheet)
        validators.validate_keyword(sheet)

    # Validate foreign key
    for pair in configs.foreign_key_validation_pairs:
        _pair = {
            "from_field": "experiment",
            "from_sheet_obj": _sheet_dict[pair["from_sheet_obj"]],
            "to_field": "name",
            "to_sheet_obj": _sheet_dict[pair["to_sheet_obj"]],
        }
        validators.validate_foreign_key(**_pair)

    # Validate "data"
    data_sheet = _sheet_dict.get("data")
    for sheet in _sheet_dict.values():
        for col in sheet.col_parsed:
            parsed_col_name_obj = sheet.col_parsed[col]
            field_list = parsed_col_name_obj.field_list
            if "data" in field_list:
                validators.validate_foreign_key(
                    col, sheet.sheet_name, "name", data_sheet
                )

    # Parse Excel sheets
    for sheet in _sheet_dict.values():
        sheet.parse()

    # Validate property, condition, identity and quantity
    for sheet in _sheet_dict.values():
        validators.validate_property(sheet)
        validators.validate_condition(sheet)
        validators.validate_identity(sheet)
        validators.validate_quantity(sheet)


# Error detection output
def output_detected_error(_sheet_dict):
    _bug_count = 0
    print(f"***********************")
    for sheet in _sheet_dict.values():
        for exception_message in sheet.errors:
            print(exception_message)
            _bug_count = _bug_count + 1
            if _bug_count >= 500:
                break
        if _bug_count >= 500:
            break

    if _bug_count == 0:
        print(f"No bugs here! Your excel sheet looks good. Start uploading now.")
    elif _bug_count < 500:
        print(f"\nYou have {_bug_count} bugs to fix.")
    elif _bug_count >= 500:
        print(
            f"\nYou have too many bugs. "
            f"Fix the 500 bugs above first and have a check again."
        )
    print(f"***********************")
    return _bug_count


# Transform and Upload parsed data
def transform_and_upload(_sheet_dict):
    # Define sheets
    experiment_sheet = _sheet_dict.get("experiment")
    data_sheet = _sheet_dict.get("data")
    file_sheet = _sheet_dict.get("file")
    material_sheet = _sheet_dict.get("material")
    mixture_component_sheet = _sheet_dict.get("mixture component")
    process_sheet = _sheet_dict.get("process")
    prerequisite_process_sheet = _sheet_dict.get("prerequisite process")
    process_ingredient_sheet = _sheet_dict.get("process ingredient")
    process_product_sheet = _sheet_dict.get("process product")

    # experiment
    experiment_objs = transformers.transform_experiment(
        group_obj,
        collection_obj,
        experiment_sheet.parsed,
        public_flag,
    )
    uploaders.upload(db, "Experiment", experiment_objs, user_uid)

    # data
    data_objs = transformers.transform_data(
        group_obj,
        experiment_objs,
        data_sheet.parsed,
        public_flag,
    )
    uploaders.upload(db, "Data", data_objs, user_uid)

    # file
    # file_objs = transformers.transform_file(
    #     group_obj,
    #     data_objs,
    #     file_sheet.parsed,
    #     public_flag,
    # )
    # uploaders.upload(db, "File", file_objs, user_uid)

    # material
    material_objs = transformers.transform_material(
        group_obj,
        data_objs,
        material_sheet.parsed,
        public_flag,
    )
    uploaders.upload(db, "Material", material_objs, user_uid)

    # mixture component
    if len(mixture_component_sheet.parsed) > 0:
        transformers.transform_components(
            material_objs,
            mixture_component_sheet.parsed,
        )
        uploaders.upload(db, "Material Component", material_objs, user_uid)

    # process
    process_objs = transformers.transform_process(
        group_obj,
        experiment_objs,
        data_objs,
        process_sheet.parsed,
        public_flag,
    )
    uploaders.upload(db, "Process", process_objs, user_uid)

    # prerequisite process
    if len(prerequisite_process_sheet.parsed) > 0:
        transformers.transform_prerequisite_process(
            process_objs,
            prerequisite_process_sheet.parsed,
        )
        uploaders.upload(db, "Prerequisite Process", process_objs, user_uid)

    # process ingredient
    transformers.transform_process_ingredient(
        process_objs,
        material_objs,
        process_ingredient_sheet.parsed,
    )
    uploaders.upload(db, "Process Ingredient", process_objs, user_uid)

    # process product
    transformers.transform_process_product(
        process_objs,
        material_objs,
        process_product_sheet.parsed,
    )
    uploaders.upload(db, "Process Product", process_objs, user_uid)


# Parse, Error Detection, Transform and Upload
bug_count = -1
sheet_dict = None
while bug_count != 0:
    sheet_dict = construct_sheet_objs()
    validate_and_parse_sheets(sheet_dict)
    bug_count = output_detected_error(sheet_dict)
    if bug_count != 0:
        input(
            "Press enter when you have saved your changes and ready to run parser again :P "
        )
transform_and_upload(sheet_dict)

# End
print("\n\nAll data was uploaded!\n")
url = collection_obj.url.replace("/api", "").strip("/")
print(f"Have a check: {url}")

print(ascii_art.thank_you.template)
input("\nPress enter to exit...")
