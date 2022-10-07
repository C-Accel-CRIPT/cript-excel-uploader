import pandas as pd


class MaterialAutoFill:

    def __init__(self):
        self.material_file_path_to_read_from = None
        self.material_file_path_to_write_to = None
        self.material_sheet_to_write_to = None
        self.all_sheets_df_dict = {}
        self.all_row_2_possible_values = None

    def read_excel_file(self, source_excel_file, ):
        """
         This method reads each sheet of the Excel file and fills up all_sheets_df_dict
         for all other methods to grab from and use
        :params source_excel_file: Excel file with vocabulary sheets
        :returns: None
        """

        excel_file = pd.ExcelFile(source_excel_file)

        # put each sheet df into the dict for other functions to use
        self.all_sheets_df_dict["material_property"] = pd.read_excel(excel_file, "material_property")
        self.all_sheets_df_dict["citation_type"] = pd.read_excel(excel_file, "citation_type")
        self.all_sheets_df_dict["condition"] = pd.read_excel(excel_file, "condition")

    def property_colon_condition(self, property_df, condition_df):
        pass

    def property_colon_citations(self, property_df, citation_df):
        pass

    def property_colon_attribute(self, property_df, citation_df):
        pass

    def write_to_dest_excel_sheet(self, df):
        pass


if __name__ == "__main__":
    material_options = MaterialAutoFill()
    material_options.read_excel_file("./excel_files/source.xlsx")
