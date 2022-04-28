import json
import os


def standardize_name(name):
    try:
        name = str(name)
        name = name.replace(" ", "").lower()
    except Exception:
        pass
    finally:
        return name


def filter_required_col(required_col_list):
    new_list = []
    for col_name in required_col_list:
        if col_name not in ["group", "collection", "type"]:
            new_list.append(col_name)
    return new_list


def read_config(executable_directory):
    file_path = os.path.join(executable_directory, "./config.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f), True
        except Exception as e:
            print(
                f"An error happened when parsing config.json, "
                f"Info: {e.__str__()}\n"
                f"Read known issues in our github readme page"
                f"(https://github.com/C-Accel-CRIPT/cript-excel-uploader/tree/yisheng-restapi-binding) "
                f"to fix the problem."
            )
            return {}, False
    else:
        return {}, False
