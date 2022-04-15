import os
import time
import traceback

import ascii_art
import sheets
import uploaders
import validators
import configs

from errors import GroupRelatedError

script_directory = os.path.dirname(os.path.abspath(__file__))
activate_this = os.path.join(script_directory, "./venv/Scripts/activate_this.py")
code = compile(open(activate_this).read(), activate_this, "exec")
exec(code, dict(__file__=activate_this))


# Display title
print(ascii_art.title.template)

token = None
db = None
while token is None:
    token = input("\nAPI token: ")
    try:
        db = uploaders.connect(token)
    except Exception as e:
        print(e.with_traceback())
        token = None

while True:
    try:
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
        while not os.path.exists(path) or os.path.splitext(path)[-1] != ".xlsx":
            if os.path.exists(path):
                print("Couldn't find the file. Try again.\n")
            else:
                print("This is not an excel file. Try again.\n")
            path = input("Excel file path: ")

        public_flag = None
        while public_flag != "y" and public_flag != "n":
            public_flag = input("\nDo you want your data to go public? y/n ---")
        public_flag = public_flag == "y"

        # Display chem art
        print(ascii_art.chem.template)
        time.sleep(1)

        bug_count = 1
        while bug_count > 0:
            # Get parameters
            param = db.keys

            # Instantiate Sheet objects
            material_sheet = sheets.MaterialSheet(path, "Define materials", param)
            experiment_sheet = sheets.ExperimentSheet(path, "Define experiments", param)
            process_sheet = sheets.ProcessSheet(path, "Define processes", param)
            processIngredient_sheet = sheets.StepIngredientSheet(
                path, "Define process ingredients", param
            )
            data_sheet = sheets.DataSheet(path, "Define raw data", param)

            # Validate Excel Sheets
            #
            sheet_dict = {
                "material_sheet": material_sheet,
                "experiment_sheet": experiment_sheet,
                "process_sheet": process_sheet,
                "processIngredient_sheet": processIngredient_sheet,
                "data_sheet": data_sheet,
            }
            # Check for reading data template

            # Validate unique key and not null value
            for sheet in sheet_dict.values():
                validators.validate_required_cols(sheet)
                validators.validate_either_or_cols(sheet)
                validators.validate_unique_key(sheet)
                validators.validate_not_null_value(sheet)
                # validators.validate_unit(sheet) # to be discussed

            # Validate foreign key
            for pair in configs.foreign_key_validation_pairs:
                pair["from_sheet_obj"] = sheet_dict[pair["from_sheet_obj"]]
                pair["to_sheet_obj"] = sheet_dict[pair["to_sheet_obj"]]
                validators.validate_foreign_key(**pair)

            for sheet in sheet_dict.values():
                for field in sheet.col_lists_dict:
                    col_list = sheet.col_lists_dict[field]
                    if len(col_list) == 2 and col_list[-1] == "data":
                        validators.validate_foreign_key(
                            field, sheet.sheet_name, "name", data_sheet
                        )

            # Parse Excel Sheets
            #
            for sheet in sheet_dict.values():
                sheet.parse()

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
                print(
                    f"No bugs here! Your excel sheet looks good. "
                    f"Start uploading now."
                )
            elif bug_count < 500:
                print(f"\nYou have {bug_count} bugs to fix.")
            elif bug_count >= 500:
                print(
                    f"\nYou have too many bugs. "
                    f"Fix the 500 bugs above first and have a check again."
                )
            print(f"***********************\n")

            reupload_flag = "y" if bug_count == 0 else None
            while reupload_flag != "y":
                reupload_flag = input(
                    f"Ready to upload again? "
                    f"Make sure you have saved the changes. y/n ---"
                )

        # Upload parsed data
        #
        group_obj = uploaders.upload_group(
            db,
            group,
        )
        print(f"***********************")
        coll_obj = uploaders.upload_collection(
            db,
            group_obj,
            collection,
            public_flag,
        )
        print(f"***********************")
        expt_objs = uploaders.upload_experiment(
            db,
            group_obj,
            coll_obj,
            experiment_sheet.parsed,
            public_flag,
        )
        print(f"***********************")
        data_objs = uploaders.upload_data(
            db,
            group_obj,
            expt_objs,
            data_sheet.parsed,
            public_flag,
        )
        print(f"***********************")
        file_objs = uploaders.upload_file(
            db,
            group_obj,
            data_objs,
            file_sheet.parsed,
            public_flag,
        )
        print(f"***********************")
        material_objs = uploaders.upload_material(
            db,
            group_obj,
            data_objs,
            material_sheet.parsed,
            public_flag,
        )
        print(f"***********************")
        process_objs = uploaders.upload_process(
            db,
            group_obj,
            expt_objs,
            process_sheet.parsed,
            public_flag,
        )
        print(f"***********************")
        step_objs = uploaders.upload_step(
            db,
            group_obj,
            process_objs,
            data_objs,
            step_sheet.parsed,
            public_flag,
        )
        print(f"***********************")
        uploaders.upload_stepIngredient(
            db,
            process_objs,
            step_objs,
            material_objs,
            stepIngredients_sheet.parsed,
        )
        print(f"***********************")
        uploaders.upload_stepProduct(
            db,
            process_objs,
            step_objs,
            material_objs,
            stepProducts_sheet.parsed,
        )
        print(f"***********************")

        # End
        print(f"\n\nAll data was uploaded successfully!")
        print(f"Have a check at {coll_obj.url}")
        time.sleep(5)
    except Exception:
        print(traceback.format_exc())
