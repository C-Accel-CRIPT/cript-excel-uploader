import re
from pprint import pprint

import pandas as pd


class Sheet:
    def __init__(self, path, sheet_name, required_columns, unique_columns):
        self.path = path
        self.sheet_name = sheet_name
        self.required_columns = required_columns
        self.unique_columns = unique_columns

        self.df = pd.read_excel(self.path, sheet_name=self.sheet_name, header=[0, 1, 2])
        self.df.dropna(how="all", inplace=True)
        self.columns = self.df.columns

    def parse(self):
        parsed_objects = {}

        for index, row in self.df.iterrows():
            parsed_object = {}
            row_key = self._get_unique_row_key(row)

            for column in self.columns:
                # Get info related to the specific cell
                cell_info = self._get_cell_info(index, row, column)

                # Check if column should be skipped
                if self._skip_column(cell_info["key"], cell_info["value"]):
                    continue

                # Convert list values (with ";" separator) to Python lists
                # Manually skip fields commonly containing semicolons
                if (
                    cell_info["value"] not in ("notes", "description", "sample_prep")
                    and isinstance(cell_info["value"], str)
                    and ";" in cell_info["value"]
                ):
                    cell_info["value"] = [
                        x.strip() for x in cell_info["value"].split(";")
                    ]

                # Identify the cell's nested parent
                parent = self._get_parent(
                    parsed_object, cell_info["nested_types"], cell_info["nested_keys"]
                )

                # Handle relation fields
                if cell_info["type"] == "relation":
                    cell_info["value"] = (cell_info["value"].strip(),)

                self._parse_cell(parent, cell_info)

            parsed_objects[row_key] = parsed_object

        return parsed_objects

    def _skip_column(self, key, value):
        """Check if a column should be skipped."""
        # Check if col starts with '#'
        if key[0] == "#":
            return True

        # Check if val empty
        if pd.isna(value):
            return True

        return False

    def _get_cell_info(self, index, row, column):
        nested_types = column[0].split(":")
        nested_keys = column[1].split(":")
        return {
            "index": index,
            "nested_types": nested_types,
            "nested_keys": nested_keys,
            "type": nested_types[-1],
            "unique_key": nested_keys[-1].strip("*"),
            "key": self._clean_key(nested_keys[-1]),
            "value": row[column],
            "unit": column[2] if "Unnamed" not in column[2] else None,
        }

    def _get_parent(self, parsed_object, column_type_list, column_key_list):
        column_len = len(column_type_list)
        if column_len == 1:
            return parsed_object

        current_parent = parsed_object
        i = 1
        while i < column_len:
            current_parent = current_parent[column_key_list[i - 1]]
            i += 1

        return current_parent

    def _parse_cell(self, parent, cell_info):
        parent.update(
            {
                cell_info["unique_key"]: {
                    "sheet": self.sheet_name,
                    "index": cell_info["index"],
                    "key": cell_info["key"],
                    "value": cell_info["value"],
                    "unit": cell_info["unit"],
                    "type": cell_info["type"],
                }
            }
        )

    def _get_unique_row_key(self, row):
        row_key = ()
        for column in self.columns:
            key = self._clean_key(column[1])
            if key in self.unique_columns:
                value = row[column].strip()
                row_key = row_key + (value,)
        return row_key

    def _clean_key(self, raw_key):
        return re.sub("\[.*\]", "", raw_key.strip("*"))
