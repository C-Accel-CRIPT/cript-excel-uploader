# python imports
import os

# 3rd party imports
import pandas as pd


def get_config_from_excel_sheet():
    # tries to read the Excel uploader if its named CRIPT_uploader_template.xlsx
    # if the user has it named differently, then it asks what is the name of your Excel file with extension
    # if it still doesn't work then it goes to exception issues and the other exception handling asks them one by one
    try:
        excel_file_name = "CRIPT_uploader_template.xlsx"
        excel_abs_path = os.path.join(os.getcwd(), excel_file_name)
        df = pd.read_excel(excel_abs_path, sheet_name="config")

    except FileNotFoundError:
        excel_file_name = input("Name of Excel file (eg. CRIPT_uploader_template.xlsx)")
        excel_abs_path = os.path.join(os.getcwd(), excel_file_name)
        df = pd.read_excel(excel_abs_path, sheet_name="config")

    return {
        "host": df["host"][0],
        "token": df["token"][0],
        "project": df["project name"][0],
        "collection": df["collection name"][0],
        "public": df["public"][0] == 1.0
    }
