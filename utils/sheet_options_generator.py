import re

import pandas as pd


def get_dict_of_all_excel_sheets(source_excel_file):
    """
    takes the whole source Excel file, gets the name of all the sheets that exist
    loops through every sheet and fills up all_sheets_dict with a df of each sheet
    and returns the dict of all sheets df
    :params source_excel_file: Excel file with vocabulary sheets
    :returns all_sheets_dict: dict filled with df of every sheet
    """

    all_sheets_dict = {}

    # loop through all sheets and add them as a df to all_sheets_dict
    excel_file = pd.ExcelFile(source_excel_file)

    for sheet_name in excel_file.sheet_names:
        # skipping the first row because the first row is the label/link for the source file
        df = pd.read_excel(excel_file, sheet_name, skiprows=[0])

        # adding metadata of sheet name into the df to be used later
        # if the sheet_name ends with a number then remove the number `attribute 1` becomes `attribute`
        df.sheet_name = re.sub(r' \d+$', '', sheet_name)

        all_sheets_dict[sheet_name] = df

    return all_sheets_dict


def get_preferred_unit(row):
    """
    checks if there is a preferred unit
    if no preferred unit then it uses the SI unit
    if no preferred unit or SI unit, then it returns an empty string

    :params row: pandas series
    :returns: string unit or an empty string
    """

    # Guard clause: handling a case that I pass in a row from a sheet
    # that doesn't have any units' column,in that case just tell me and do nothing
    if "Preferred unit" not in row and "SI unit" not in row:
        return

    # making them into variables, so I don't have to keep repeating them
    preferred_unit = row["Preferred unit"]
    si_unit = row["SI unit"]

    # has a preferred unit ie not "", "None", nor nan, then return preferred_unit
    if (
            preferred_unit != ""
            and preferred_unit != "None"
            and not pd.isna(preferred_unit)
    ):
        return preferred_unit

    # does not have preferred unit, but has SI unit
    elif (
            preferred_unit == "" or preferred_unit == "None" or pd.isna(preferred_unit)
    ) and (si_unit != "" and si_unit != "None" and not pd.isna(si_unit)):
        return si_unit

    # si unit and preferred unit are both empty or None
    elif (
            preferred_unit == "" or preferred_unit == "None" or pd.isna(preferred_unit)
    ) and (si_unit == "" or si_unit == "None" or pd.isna(si_unit)):
        return ""

    # if somehow all the if cases are passed,
    # then I need to know about it and create new conditions to capture them
    else:
        raise Exception(
            f'hit else for {row["Name"]}; preferred_unit: {preferred_unit}; si_unit: {si_unit}'
        )


def get_instructions(row, sheet_name):
    """
    takes a row and gives back the instructions

    :params row: padnas series
    :returns instructions: a string that represents the instructions for that column
    """

    # gave the same instruction for all relation fields
    # e.g.: "Pick value from *name column of data sheet"
    if sheet_name == "relation":
        instruction = f"Pick value from *name column of {row['Name']} sheet"
        return instruction

    if (sheet_name == "attribute") and (row["Name"] == "uncertainty_type"):
        return "Pick uncertainty type from criptapp.org controlled vocabulary"

    # guard clause that returns empty string, if there is no description column in that sheet
    if "Description" not in row:
        return ""

    # if "Description" column exists, then instruction is description column
    if "Description" in row:
        return row["Description"]


def get_new_df():
    """
    creates a new DF with columns needed for the Excel file options
    returns: pandas dataframe object
    """

    # return df with:
    # Column 1: "category",  Column 2: "Name", Column 3: "unit", Column 4: instructions
    return pd.DataFrame(columns=["category", "Name", "unit", "instructions"])


def single_options(sheet_df):
    """
    takes a single Excel sheet df, and gets the Row 1 value, Row 2, value, unit, and description
    appends them to a df on every loop
    returns the df to be appended to the full list of all possible options

    :params sheet_df: pandas dataframe
    :returns df: pandas dataframe
    """

    # df that I will fill for single options
    df = get_new_df()

    # loop through and fill up the DF in the columns of
    # "category", "Name", "unit", "instructions"
    for index, row in sheet_df.iterrows():
        df.loc[index, "category"] = sheet_df.sheet_name
        df.loc[index, "Name"] = row["Name"]
        df.loc[index, "unit"] = get_preferred_unit(row)
        df.loc[index, "instructions"] = get_instructions(row, sheet_df.sheet_name)

    return df


def sheet1_colon_sheet2(sheet1_df, sheet2_df):
    """
    this function takes 2 Excel sheet df and returns a df with sheet1:sheet2

    :params sheet1_df: Excel sheet pandas dataframe object
    :params sheet2_df: Excel sheet pandas dataframe object

    :returns df: pandas dataframe object with columns of "category, Name, unit, instructions"
    """

    # df that I will fill for single options
    df = get_new_df()

    # counter to know how which empty row to write to
    row_number = 0

    # using index of i1 and i2 because it wasn't working without them
    for i1, sheet1_row in sheet1_df.iterrows():
        for i2, sheet2_row in sheet2_df.iterrows():
            df.loc[
                row_number, "category"
            ] = f"{sheet1_df.sheet_name}:{sheet2_df.sheet_name}"
            df.loc[row_number, "Name"] = f"{sheet1_row['Name']}:{sheet2_row['Name']}"
            df.loc[row_number, "unit"] = get_preferred_unit(sheet2_row)
            df.loc[row_number, "instructions"] = get_instructions(
                sheet2_row, sheet2_df.sheet_name
            )

            # increment counter to start on the next row that is blank
            row_number += 1

    return df


def write_to_excel(df, output_path, output_file_name, sheet_name):
    """
    takes a df that we want to write to an Excel sheet.
    sorts the df based on the Row 2 column to sort it alphabetically for the user
    to easily find what they need.
    we take the output path Eg. "./excel_files/"
    and we add to it the output_file_name to get "./excel_files/output.xlsx"
    and we write the contents of df to "./excel_files/output.xlsx" to the sheet_name we want,
    and we remove the default index column that Pandas comes with by specifying
    index=False

    :params df: pandas dataframe object that will be written to an Excel sheet
    :params output_path: a string path of where we want to write the Excel file to
    :params output_file_name: what we want to call the file when it is written
    :params sheet_name: the sheet we want to write to
    :returns: None
    """

    # sort the df based on Names
    df = df.sort_values("Name")

    df.to_excel(output_path + output_file_name, sheet_name=sheet_name, index=False)

    print(f"created all options in {output_path}{output_file_name}")


def create_one_option_df():
    """
    this function is essentially used to create a single option without any loops or nesting
    it basically creates a df like `use_existing`, but in a nice function where you don't have to think about it
    just pass in the things you need and get your df and put it in the other dfs

    ```python
    update_existing_option = get_new_df()
    update_existing_option.loc[0, "category"] = "property"
    update_existing_option.loc[0, "Name"] = "use_existing"
    update_existing_option.loc[0, "unit"] = ""
    update_existing_option.loc[0, "instructions"] = "Mark TRUE to update already saved material in CRIPT"
    ```
    """
    one_option = get_new_df()
    one_option.loc[0, "category"] = "relation"
    one_option.loc[0, "name"] = "citation"
    one_option.loc[0, "unit"] = ""
    one_option.loc[0, "instructions"] = "Pick a value from *name column of citation sheet"


def create_material_options():
    # shows where to read all the options for the Excel file
    all_sheets_df = get_dict_of_all_excel_sheets("excel_files/material_source.xlsx")

    # the df that holds all the options. making a df with all needed columns
    full_options_df = get_new_df()

    # creates all property keys
    material_identifiers = single_options(all_sheets_df["identifiers"])
    material_properties = single_options(all_sheets_df["property"])

    # creates all fields that can be nested under property e.g. property:uncertainty
    material_property_colon_attributes = sheet1_colon_sheet2(
        all_sheets_df["property"], all_sheets_df["attribute"]
    )

    # creates all fields that can have a relation under property e.g. property:data
    material_property_colon_relation = sheet1_colon_sheet2(
        all_sheets_df["property"], all_sheets_df["relation"]
    )

    # creates all property:conditions df
    material_property_colon_condition = sheet1_colon_sheet2(
        all_sheets_df["property"], all_sheets_df["condition"]
    )

    # creates all property:type df
    material_property_colon_type = sheet1_colon_sheet2(
        all_sheets_df["property"], all_sheets_df["type"]
    )

    # creates all property:type df
    material_property_colon_method = sheet1_colon_sheet2(
        all_sheets_df["property"], all_sheets_df["method"]
    )

    # update existing options
    update_existing_option = get_new_df()
    update_existing_option.loc[0, "category"] = "property"
    update_existing_option.loc[0, "Name"] = "use_existing"
    update_existing_option.loc[0, "unit"] = ""
    update_existing_option.loc[0, "instructions"] = "Mark TRUE to update already saved material in CRIPT"

    print(update_existing_option)

    # the full list of options for material sheet to be written to Excel
    full_options_df = pd.concat(
        [
            full_options_df,
            material_identifiers,
            material_properties,
            material_property_colon_attributes,
            material_property_colon_condition,
            material_property_colon_relation,
            material_property_colon_type,
            material_property_colon_method,
            update_existing_option
        ]
    )

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(full_options_df)

    # write all options to an Excel file
    write_to_excel(full_options_df, "./excel_files/", "material_output.xlsx", "material options")


def create_process_options():
    # shows where to read all the options for the Excel file
    all_sheets_df = get_dict_of_all_excel_sheets("excel_files/process_source.xlsx")

    # the df that holds all the options. making a df with all needed columns
    full_options_df = get_new_df()

    # process property
    process_property = single_options(all_sheets_df["property"])

    # property:method
    property_colon_method = sheet1_colon_sheet2(all_sheets_df["property"], all_sheets_df["method"])

    # process condition
    process_condition = single_options(all_sheets_df["condition"])

    # property:condition
    property_colon_condition = sheet1_colon_sheet2(all_sheets_df["property"], all_sheets_df["condition"])

    # the full list of options for material sheet to be written to Excel
    full_options_df = pd.concat(
        [
            full_options_df,
            process_property,
            property_colon_method,
            process_condition,
            property_colon_condition
        ]
    )

    # write all options to an Excel file
    write_to_excel(full_options_df, "./excel_files/", "process_output.xlsx", "process options")


def create_computational_process_options():
    all_sheets_df = get_dict_of_all_excel_sheets("excel_files/computational_process.xlsx")
    full_options_df = get_new_df()

    properties = single_options(all_sheets_df["property"])
    conditions = single_options(all_sheets_df["condition"])

    property_colon_condition = sheet1_colon_sheet2(all_sheets_df["property"], all_sheets_df["condition"])

    full_options_df = pd.concat(
        [
            full_options_df,
            properties,
            conditions,
            property_colon_condition
        ]
    )

    write_to_excel(full_options_df, "./excel_files/", "computational_process_output.xlsx",
                   "computational_process options")


def create_software_configuration_options():
    all_sheets_df = get_dict_of_all_excel_sheets("excel_files/software_configuration.xlsx")
    full_options_df = get_new_df()

    algorithm_colon_parameter = sheet1_colon_sheet2(all_sheets_df["attribute"], all_sheets_df["attribute"])

    full_options_df = pd.concat(
        [
            full_options_df,
            algorithm_colon_parameter
        ]
    )

    write_to_excel(full_options_df, "./excel_files/", "software_configuration_output.xlsx",
                   "software_configuration_options")


if __name__ == "__main__":
    # create_material_options()
    # create_process_options()
    # create_computational_process_options()
    create_software_configuration_options()
