import json
import os

import pandas as pd


def standardize_name(name):
    """
    Standardize foreign key names. Remove space and make every char lower case
    :param name:
    :return:
    """
    if name is None or pd.isna(name):
        return name

    if isinstance(name, str) or isinstance(name, int) or isinstance(name, float):
        name = str(name)
        name = name.replace(" ", "").lower()
    return name


def filter_required_col(required_col_list):
    """
    Remove unnecessary column name (which has already defined in excel sheet level) in unique_together field
    :param required_col_list:
    :return:
    """
    new_list = []
    for col_name in required_col_list:
        if col_name not in ["group", "collection", "type"]:
            new_list.append(col_name)
    return new_list


def read_config(executable_directory, config_file_name="config.json"):
    """
    Try to read case_config_1_true.json file
    :param executable_directory: the directory where executable file and config file located
    :param config_file_name: file name of config file, must be json file
    :return: (param):(value) dict and bool result of whether config file exists
    :rtype: dict, bool
    """
    # File path, same directory as where executable file is in
    file_path = os.path.join(executable_directory, "./" + config_file_name)
    if os.path.exists(file_path) and os.path.splitext(file_path)[-1] == ".json":
        try:
            with open(file_path, "r") as f:
                return json.load(f), True
        except Exception as e:
            print(
                f"An error happened when parsing case_config_1_true.json, "
                f"Info: {e.__str__()}\n"
                f"Read known issues in our github readme page"
                f"(https://github.com/C-Accel-CRIPT/cript-excel-uploader/tree/yisheng-restapi-binding) "
                f"to fix the problem."
            )
            return {}, False
    else:
        return {}, False
