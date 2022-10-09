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
    :returns: a string that has the preferred units or an empty string
    """
    preferred_unit = row["Preferred unit"]
    si_unit = row["SI unit"]

    # has a preferred unit
    if preferred_unit is not "" and preferred_unit is not "None":
        return preferred_unit

    # does not have preferred unit, but has SI unit
    elif (preferred_unit is "" or preferred_unit is "None") and (si_unit is not "" and si_unit is not "None"):
        return si_unit

    # si unit and preferred unit are both empty or none
    elif (preferred_unit is "" or preferred_unit is "None") and (si_unit is "" or si_unit is "None"):
        return ""


def single_options(sheet_df):
    """
    takes a single Excel sheet df, and gets the Row 1 value, Row 2, value, unit, and description
    appends them to a df on every loop
    returns the df to be appended to the full list of all possible options

    :params sheet_df: pandas dataframe
    :returns df: pandas dataframe
    """
    df = pd.DataFrame()

    # TODO I don't think this way of appending to the df is working
    for row in sheet_df.iterrows():
        df["Row 1 Value"] = sheet_df.sheet_name
        df["Row 2 Value"] = row[1]["Name"]

        # be sure you do not have "" or "None" in preferred values
        # can probably add a check for having 2 preferred values as well
        # if there is no preferred value see if there is SI Value instead
        # use get_preferred_unit( ) here instead
        df["unit"] = row[1]["Preferred unit"]
        df["description"] = row[1]["Description"]


# TODO make this abstract so it can work for all of them
def property_colon_condition(property_df, condition_df):
    all_property_condition = pd.DataFrame()

    for property_row in property_df.iterrows():
        for condition_row in condition_df.iterrows():
            df = pd.DataFrame()
            df["Row 1 Value"] = condition_df.sheet_name
            df["Row 2 Value"] = f"{property_row[1].iloc.name}:{condition_row[1].iloc.name}"


def write_to_dest_excel_sheet(df):
    pass


if __name__ == "__main__":
    all_sheets_df = get_all_excel_sheets("./excel_files/source.xlsx")
    full_options_df = pd.DataFrame()

    # working on getting the single version working first
    single_options(all_sheets_df["property"])
