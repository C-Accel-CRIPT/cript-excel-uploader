import pandas as pd

import configs
from errors import (
    DataAssignmentError,
    UnsupportedFieldName,
)


class Sheet:
    """The base Sheet class."""

    def __init__(self, path, sheet_name, param):
        self.path = path
        self.sheet_name = sheet_name
        self.param = param
        self.df = None

        self.cols = None
        self.required_cols = configs.required_cols[self.sheet_name]
        self.either_or_cols = configs.either_or_cols[self.sheet_name]
        self.not_null_cols = configs.required_cols[self.sheet_name]
        self.list_fields = configs.list_fields[self.sheet_name]
        self.col_lists_dict = {}
        self.col_type = {}

        self.unique_keys = configs.unique_keys[self.sheet_name]
        self.unique_keys_dict = {}
        self.foreign_keys = configs.foreign_keys[self.sheet_name]
        self.foreign_keys_dict = {}

        self.unit_dict = {}

        self.errors = []
        self.has_error = False

    def _read_file(self):
        try:
            self.df = pd.read_excel(self.path, sheet_name=self.sheet_name)
        except ValueError:
            print(f"Worksheet [{self.sheet_name}] not found in your excel file.")

    def _data_preprocess(self):
        if self.df is None:
            return None

        # Drop NaN Columns:
        self.df.dropna(axis=1, how="all", inplace=True)

        # Drop Commented Columns
        for col in self.df.columns:
            if col[0] == "#":
                self.df = self.df.drop(col, axis=1)

        # Clean Col Name
        self.cols = [col.replace("*", "") for col in self.df.columns]
        self.df.columns = self.cols

        # Create Col List
        for col in self.cols:
            self.col_lists_dict[col] = col.split(":")

        # Standardize and Categorize Field
        for col in self.col_lists_dict:
            col_list = self.col_lists_dict[col]
            for i in range(len(col_list)):
                col_list[i] = self._standardize_and_categorize_field(col_list, i)

            self.col_lists_dict[col] = col_list

        # Create Unit Dict
        for col in self.cols:
            if pd.isna(self.df.loc[0, col]):
                self.unit_dict[col] = None
            else:
                self.unit_dict[col] = self.df.loc[0, col].strip()

        # Drop Unit Row
        self.df.drop(labels=0, axis=0, inplace=True)
        # Drop NaN Rows
        self.df.dropna(axis=0, how="all", inplace=True)

        # Convert id to Integer
        for col in self.cols:
            if col[-3:] == "_id":
                self.df = self.df.astype({col: "int"})
            if col in configs.float_cols[self.sheet_name]:
                self.df = self.df.astype({col: "float"})

        # Remove Space, Convert id to Integer, Handle List Fields
        for index, row in self.df.iterrows():
            for col in self.cols:
                value = row[col]
                if not pd.isna(value):
                    # Remove Space
                    if isinstance(value, str):
                        value = value.strip()
                        value = value.strip("\u202a")
                self.df.loc[index, col] = value

        # Create Foreign Key Dict
        for col in self.foreign_keys:
            self.foreign_keys_dict[col] = {}
            #! display index as row_index/row_number
            for index, row in self.df.iterrows():
                value = row[col]
                if value is not None:
                    _value = str(value).replace(" ", "").lower()
                self.foreign_keys_dict[col].update({_value: [value, index]})

    def _standardize_and_categorize_field(self, col_list, i):
        """
        Convert a field to the standardized version

        :return: standardized param name
        :rtype: str
        """
        field = col_list[i]
        # If field has already existed
        if field in self.col_type:
            return field

        # Foreign keys
        if field in self.foreign_keys:
            self.col_type.update({field: "foreign_key"})
            return field

        # Base cols
        for base_node in configs.base_nodes.get(self.sheet_name):
            if field.replace(base_node + "-", "") in configs.base_cols.get(base_node):
                self.col_type.update({field: base_node + "-base"})
                return field

        # Data keys
        if field == "data":
            self.col_type.update({field: "data"})
            return field

        # Identifier Keys
        iden_key = "material-identifier"
        for iden in self.param[iden_key]:
            if field == iden["name"]:
                self.col_type.update({iden["name"]: "iden"})
                return iden["name"]

        # Property Keys
        prop_key = configs.sheet_name_to_prop_key.get(self.sheet_name)
        if prop_key is not None:
            for prop in self.param[prop_key]:
                if field == prop["name"]:
                    self.col_type.update({prop["name"]: "prop"})
                    return prop["name"]

        # Condition Keys
        cond_key = "condition-key"
        for cond in self.param[cond_key]:
            if field == cond["name"]:
                self.col_type.update({cond["name"]: "cond"})
                return cond["name"]

        quan_key = "quantity-key"
        for quan in self.param[quan_key]:
            if field == quan["name"]:
                self.col_type.update({quan["name"]: "quantity"})
                return quan["name"]

        # print(f"error:{field},sheet:{self.sheet_name}")
        exception = UnsupportedFieldName(field, col_list, self.sheet_name)
        self.errors.append(exception.__str__())

    def _parse_data(self, col_list, parsed_object, value):
        """
        Parse a data column and attach to it's appropriate parsed object.
        Currently used in material sheet and process sheet

        :param col_list: list generated by splitting column into separate fields (e.g., density:temp --> [density, temp])
        :type col_list: list
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        :param value: name of something in data sheet
        :type value: str
        :raises: ValueDoesNotExist: can't find the data of the material from data sheet according to input name.
        :raises: DataAssignmentError: data is not applied to a prop or cond (e.g., molar_mass:data)
        """
        # Ensure the data is being applied to something
        if len(col_list) == 1:
            exception = DataAssignmentError(
                col_list=col_list,
                sheet=self.sheet_name,
                type=1,
            )
            self.errors.append(exception.__str__())
            return None

        # Check if data should be applied to a property or condition
        prev_field = col_list[-2]
        _type = self.col_type.get(prev_field)
        if _type == "prop" or _type == "cond":
            parent = parsed_object[_type][prev_field]
            parent["data"] = value.replace(" ", "").lower()
        else:
            exception = DataAssignmentError(
                col_list=col_list,
                sheet=self.sheet_name,
                type=2,
            )
            self.errors.append(exception.__str__())
            return None

    def _parse_prop(self, col, value, parsed_object):
        """
        Parse a property column with it's associated standard units and attributes.
        Currently used in material sheet and process sheet

        :param value: value of the reagent/material's property
        :type value: str
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        """
        # Create property dict
        field = self.col_lists_dict[col][-1]
        if len(self.col_lists_dict[col]) == 1:
            parsed_object["prop"].update(
                {
                    field: {
                        "key": field,
                        "value": value,
                        "unit": self.unit_dict[col],
                        "cond": {},
                        "data": {},
                    }
                }
            )

    def _parse_cond(self, col, value, parsed_object):
        """
        Parse a condition column with it's associated standard units.
        Currently used in data sheet, material sheet and process sheet

        :param value: value of the reagent/material's condition
        :type value: str
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        """
        # Check whether it's a property condition
        field = self.col_lists_dict[col][-1]
        if len(self.col_lists_dict[col]) == 1:
            # print("Meet a condition")
            parent = parsed_object
        else:
            # print("Meet a prop condition")
            prop_field = self.col_lists_dict[col][-2]
            parent = parsed_object["prop"][prop_field]

        # Create condition dict
        parent["cond"].update(
            {
                field: {
                    "key": field,
                    "value": value,
                    "unit": self.unit_dict[col],
                    "data": {},
                }
            }
        )

    def _replace_field(self, columns, raw_key, replace_key):
        output = []
        for i in range(len(columns)):
            if raw_key == columns[i]:
                output.append(replace_key)
            else:
                output.append(columns[i])
        return output


class ExperimentSheet(Sheet):
    """Experiment Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_experiment = {
                "base": {},
                "index": index + 2,
                "name": row["name"],
            }
            experiment_std_name = row["name"].replace(" ", "").lower()
            for col in self.cols:
                # Define value and field
                value = row[col]
                if pd.isna(value):
                    continue

                # Populate parsed_experiment dict
                if col in configs.base_cols["experiment"]:
                    parsed_experiment["base"][col] = value

            self.parsed[experiment_std_name] = parsed_experiment

        return self.parsed


class MixtureComponentSheet(Sheet):
    """MixtureComponent Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_mixture = {
                "index": index + 2,
                "name": row["components"],
            }

            material_std_name = row["material"].replace(" ", "").lower()
            if material_std_name not in self.parsed:
                self.parsed[material_std_name] = {}
            self.parsed[material_std_name].addend(parsed_mixture)

        return self.parsed


class DataSheet(Sheet):
    """Data Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        # will remove later
        self.df.columns = self._replace_field(self.df.columns, "*data_type", "type")

        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_datum = {
                "base": {},
                "experiment": None,
                "index": index + 2,
                "name": row["name"],
            }
            data_std_name = row["name"].replace(" ", "").lower()
            for col in self.cols:
                # Define value and field
                field = self.col_lists_dict[col][-1]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys
                if field in self.foreign_keys:
                    parsed_datum[field] = value

                # Populate parsed_datum dict
                if col in configs.base_cols.get("data"):
                    parsed_datum["base"][field] = value

            self.parsed[data_std_name] = parsed_datum

        return self.parsed


class FileSheet(Sheet):
    """File Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        # will remove later
        self.df.columns = self._replace_field(self.df.columns, "*path", "source")
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_file = {
                "base": {},
                "index": index + 2,
            }
            for col in self.cols:
                # Define value and field
                field = self.col_lists_dict[col][-1]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys field
                if field in self.foreign_keys:
                    parsed_file.update({field: value})

                # Populate parsed_datum dict
                if col in configs.base_cols.get("file"):
                    parsed_file["base"][field] = value

            data_std_name = row["data"].replace(" ", "").lower()
            if data_std_name not in self.parsed:
                self.parsed[data_std_name] = []
            self.parsed[data_std_name].append(parsed_file)

        return self.parsed


class MaterialSheet(Sheet):
    """Material Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_material = {
                "material-base": {},
                "iden": {},
                "prop": {},
                "cond": {},
                "index": index + 2,
                "name": row["name"],
            }
            material_std_name = row["name"].replace(" ", "").lower()
            for col in self.cols:
                # Define value and field
                col_list = self.col_lists_dict[col]
                field = self.col_lists_dict[col][-1]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle data
                if field == "data":
                    self._parse_data(col_list, parsed_material, value)

                # Handle material base fields
                if self.col_type.get(field) == "material-base":
                    parsed_material["material-base"][field] = value

                # Handle identity base fields
                if self.col_type.get(field) == "iden":
                    parsed_material["iden"][field] = value

                # Handle properties
                if self.col_type.get(field) == "prop":
                    self._parse_prop(col, value, parsed_material)

                # Handle conditions
                if self.col_type.get(field) == "cond":
                    self._parse_cond(col, value, parsed_material)

                self.parsed[material_std_name] = parsed_material

        return self.parsed


class ProcessSheet(Sheet):
    """Process Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_process = {
                "base": {},
                "index": index + 2,
                "name": row["name"],
            }
            process_std_name = row["name"].replace(" ", "").lower()
            for col in self.cols:
                # Define value and field
                field = self.col_lists_dict[col][-1]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys
                if field in self.foreign_keys:
                    parsed_process[field] = value

                # Handle base process fields
                if col in configs.base_cols.get("process"):
                    parsed_process["process-base"][field] = value

            self.parsed[process_std_name] = parsed_process

        return self.parsed


class DependentProcessSheet(Sheet):
    """MixtureComponent Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_dependency = {
                "index": index + 2,
                "name": row["dependent_processes"],
            }

            process_std_name = row["process"].replace(" ", "").lower()
            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = {}
            self.parsed[process_std_name].addend(parsed_dependency)

        return self.parsed


class StepIngredientSheet(Sheet):
    """StepIngredient Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self._create_helper_cols()
        self.parsed = {}

    def _create_helper_cols(self):
        if self.df is None:
            return None

        for index, row in self.df.iterrows():
            _value = (
                "".join(self.df.loc[index, "process"])
                .join(":")
                .join(str(self.df.loc[index, "step_id"]))
            )
            self.df.loc[index, "process:step_id"] = _value

            _value = _value.join(":").join(self.df.loc[index, "ingredient"])
            self.df.loc[index, "process:step_id:ingredient"] = _value

            self.df.loc[index, "ingredient-material"] = None
            self.df.loc[index, "ingredient-step"] = None
            _list = self.df.loc[index, "ingredient"].split(":")
            # Data assign error check
            if len(_list) == 1:
                self.df.loc[index, "ingredient-material"] = _list[0]
            if len(_list) == 2:
                self.df.loc[index, "ingredient-step"] = (
                    "".join(_list[0]).join(":").join(_list[1])
                )

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_ingredient = {
                "base": {},
                "quantity": {},
            }
            process_std_name = row["process"].replace(" ", "").lower()
            step_id = row["step_id"]
            for col in self.cols:
                # Define value and field
                field = self.col_lists_dict[col][-1]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign key
                if field in self.foreign_keys:
                    parsed_ingredient[field] = value

                if col in configs.base_cols.get("materialIngredient"):
                    parsed_ingredient["base"][field] = value

                # Handle process ingredient fields
                if self.col_type[col] == "quantity":
                    # Add quantity field with units
                    parsed_ingredient["quantity"][field] = {
                        "key": field,
                        "value": value,
                        "unit": self.unit_dict[col],
                    }

            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = {}
            if step_id not in self.parsed[process_std_name]:
                self.parsed[process_std_name][step_id] = []
            self.parsed[process_std_name][step_id].append(parsed_ingredient)

        return self.parsed


class StepProductSheet(Sheet):
    """StepProduct Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self._create_helper_cols()
        self.parsed = {}

    def _create_helper_cols(self):
        if self.df is None:
            return None

        for index, row in self.df.iterrows():
            _value = (
                "".join(self.df.loc[index, "process"])
                .join(":")
                .join(str(self.df.loc[index, "step_id"]))
            )
            self.df.loc[index, "process:step_id"] = _value

            _value = _value.join(":").join(self.df.loc[index, "product"])
            self.df.loc[index, "process:step_id:product"] = _value

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_product = {}
            process_std_name = row["process"].replace(" ", "").lower()
            step_id = row["step_id"]
            for col in self.cols:
                # Define value and field
                field = self.col_lists_dict[col][-1]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys
                if field in self.foreign_keys:
                    parsed_product[field] = value

            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = {}
            if step_id not in self.parsed[process_std_name]:
                self.parsed[process_std_name][step_id] = []
            self.parsed[process_std_name][step_id].append(parsed_product)

        return self.parsed
