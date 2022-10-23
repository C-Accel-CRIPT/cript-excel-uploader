import pandas as pd


# TODO this needs to be renamed because it is very unintuitive
def get_all_excel_sheets(source_excel_file):
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
        df = pd.read_excel(excel_file, sheet_name)

        # adding metadata of sheet name into the df to be used later
        df.sheet_name = sheet_name

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
    preferred_unit = row["Preferred unit"]
    si_unit = row["SI unit"]

    # has a preferred unit ie not "", "None", nor nan
    if preferred_unit != "" and preferred_unit != "None" and not pd.isna(preferred_unit):
        return preferred_unit

    # does not have preferred unit, but has SI unit
    elif (preferred_unit == "" or preferred_unit == "None" or pd.isna(preferred_unit)) and (
            si_unit != "" and si_unit != "None" and not pd.isna(si_unit)):
        return si_unit

    # si unit and preferred unit are both empty or none
    elif (preferred_unit == "" or preferred_unit == "None" or pd.isna(preferred_unit)) and (
            si_unit == "" or si_unit == "None" or pd.isna(si_unit)):
        return ""
    else:
        raise Exception(f'hit else for {row["Name"]}; preferred_unit: {preferred_unit}; si_unit: {si_unit}')


def get_new_df():
    row_1_value = "Row 1 Value"
    row_2_value = "Row 2 Value"
    unit = "unit"
    instructions = "instructions"

    df = pd.DataFrame(columns=[row_1_value, row_2_value, unit, instructions])
    return df


def single_options(sheet_df):
    """
    takes a single Excel sheet df, and gets the Row 1 value, Row 2, value, unit, and description
    appends them to a df on every loop
    returns the df to be appended to the full list of all possible options

    :params sheet_df: pandas dataframe
    :returns df: pandas dataframe
    """
    row_1_value = "Row 1 Value"
    row_2_value = "Row 2 Value"
    unit = "unit"
    instructions = "instructions"

    df = get_new_df()

    for index, row in sheet_df.iterrows():
        df.loc[index, row_1_value] = sheet_df.sheet_name
        df.loc[index, row_2_value] = row["Name"]
        df.loc[index, unit] = get_preferred_unit(row)
        df.loc[index, instructions] = row["Description"]

    return df


def sheet1_colon_sheet2(sheet1_df, sheet2_df):
    df = pd.DataFrame()

    row_number = 0

    for i1, sheet1_row in sheet1_df.iterrows():
        for i2, sheet2_row in sheet2_df.iterrows():
            df.loc[row_number, "Row 1 Value"] = f"{sheet1_df.sheet_name}:{sheet2_df.sheet_name}"
            df.loc[row_number, "Row 2 Value"] = f"{sheet1_row['Name']}:{sheet2_row['Name']}"
            df.loc[row_number, "unit"] = get_preferred_unit(sheet2_row)
            df.loc[row_number, "instructions"] = sheet2_row['Description']

            row_number += 1

    return df


def write_to_dest_excel_sheet(df):
    pass


if __name__ == "__main__":
    all_sheets_df = get_all_excel_sheets("./excel_files/source.xlsx")
    # this is the final DF that will be written to the .xlsx file

    full_options_df = get_new_df()

    properties = single_options(all_sheets_df["property"])

    property_colon_condition = sheet1_colon_sheet2(all_sheets_df["property"], all_sheets_df["condition"])

    # print(property_colon_condition.shape)

    full_options_df = pd.concat([full_options_df, property_colon_condition])

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(full_options_df)
