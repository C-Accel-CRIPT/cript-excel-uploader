import pandas as pd

import configs
from errors import (
    UnsupportedColumnName,
    ColumnParseError,
)
from util import (
    standardize_name,
)
from parser import (
    parse_col_name,
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
        self.col_parsed = {}

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

        # Clean Column Name
        self.cols = [col.replace("*", "") for col in self.df.columns]
        self.df.columns = self.cols

        # Parse Column Name
        for col in self.cols:
            try:
                self.col_parsed[col] = parse_col_name(col)
            except ColumnParseError as e:
                exception = UnsupportedColumnName(
                    col=col,
                    sheet=self.sheet_name,
                    message=e.__str__(),
                )
                self.errors.append(exception.__str__())
                self.col_parsed[col] = None

        # Standardize and Categorize Field
        for col in self.col_parsed:
            parsed_col_name_obj = self.col_parsed[col]
            self._standardize_and_categorize_field(parsed_col_name_obj)

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

        # Remove Space
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

    def _standardize_and_categorize_field(self, parsed_column_name_obj):
        """
        Convert a field to the standardized version

        :return: standardized param name
        :rtype: str
        """
        field_list = parsed_column_name_obj.field_list
        field_type_list = parsed_column_name_obj.field_type_list
        origin_col = parsed_column_name_obj.origin_col
        for i in range(len(field_list)):
            field = field_list[i]
            prev_field_type = field_type_list[i - 1] if i > 0 else None
            found_tag = False

            if field is None:
                field_type_list.append(None)
                found_tag = True

            # Foreign keys
            if not found_tag and field in self.foreign_keys:
                field_type_list.append("foreign_key")
                found_tag = True

            # Base cols
            for base_node in configs.base_nodes.get(self.sheet_name):
                if not found_tag and field in configs.base_cols.get(base_node):
                    field_type_list.append("base")
                    found_tag = True

            # Data keys
            if not found_tag and field == "data":
                field_type_list.append("data")
                found_tag = True

            # Identifier Keys
            iden_key = "material-identifier-key"
            for iden in self.param[iden_key]:
                if not found_tag and field == iden["name"]:
                    field_type_list.append("iden")
                    found_tag = True

            # Property Keys
            prop_key = configs.sheet_name_to_prop_key.get(self.sheet_name)
            if prop_key is not None:
                for prop in self.param[prop_key]:
                    if not found_tag and field == prop["name"]:
                        field_type_list.append("prop")
                        found_tag = True

            # Condition Keys
            cond_key = "condition-key"
            for cond in self.param[cond_key]:
                if not found_tag and field == cond["name"]:
                    field_type_list.append("cond")
                    found_tag = True

            quan_key = "quantity-key"
            for quan in self.param[quan_key]:
                if not found_tag and field == quan["name"]:
                    field_type_list.append("quan")
                    found_tag = True

            if prev_field_type == "prop":
                for prop_attr in configs.base_cols["property"]:
                    if not found_tag and field == prop_attr:
                        field_type_list.append("prop-attr")
                        found_tag = True

            if prev_field_type == "cond":
                for cond_attr in configs.base_cols["condition"]:
                    if not found_tag and field == cond_attr:
                        field_type_list.append("cond-attr")
                        found_tag = True

            if not found_tag:
                exception = UnsupportedColumnName(
                    col=origin_col,
                    field=field,
                    sheet=self.sheet_name,
                )
                self.errors.append(exception.__str__())

    def _parse_prop(self, col, start_index, value, parsed_object):
        """
        Parse a property column with it's associated standard units and attributes.
        Currently used in material sheet and process sheet

        :param value: value of the reagent/material's property
        :type value: str
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        [prop, prop:cond, prop:data, prop:attr]
        """
        parsed_column_name_obj = self.col_parsed[col]
        field_list = parsed_column_name_obj.field_list
        field_type_list = parsed_column_name_obj.field_type_list
        identifier = parsed_column_name_obj.identifier

        field = field_list[start_index]
        field_nested = field_list[start_index + 1]
        field_nested_type = field_type_list[start_index + 1]

        # Create property dict
        if "prop" not in parsed_object:
            parsed_object["prop"] = {}
        if field not in parsed_object["prop"]:
            parsed_object["prop"][field] = {}
        if identifier not in parsed_object["prop"][field]:
            parsed_object["prop"][field][identifier] = {
                "attr": {},
                "cond": {},
                "data": [],
            }

        parent = parsed_object["prop"][field][identifier]

        # prop:None
        if field_nested_type is None:
            parent["attr"]["key"] = field
            parent["attr"]["value"] = value
            parent["attr"]["unit"] = self.unit_dict[col]
        # prop:attr
        elif field_nested_type == "prop-attr":
            parent["attr"][field_nested] = value
        # prop:data
        elif field_nested_type == "data":
            parent["data"].append(standardize_name(value))
        # prop:cond
        elif field_nested_type == "cond":
            self._parse_cond(col, start_index + 1, value, parent)

    def _parse_cond(self, col, start_index, value, parsed_object):
        """
        Parse a condition column with it's associated standard units.
        Currently used in data sheet, material sheet and process sheet

        :param value: value of the reagent/material's condition
        :type value: str
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        [cond, cond:attr, cond:data]
        """
        parsed_column_name_obj = self.col_parsed[col]
        field_list = parsed_column_name_obj.field_list
        field_type_list = parsed_column_name_obj.field_type_list
        identifier = parsed_column_name_obj.identifier

        field = field_list[start_index]
        field_nested = field_list[start_index + 1]
        field_nested_type = field_type_list[start_index + 1]

        # create condition dict
        if "cond" not in parsed_object:
            parsed_object["cond"] = {}
        if field not in parsed_object["cond"]:
            parsed_object["cond"][field] = {}
        if identifier not in parsed_object["cond"][field]:
            parsed_object["cond"][field][identifier] = {
                "attr": {},
                "data": [],
            }

        parent = parsed_object["cond"][field][identifier]

        # cond:None
        if field_nested_type is None:
            parent["attr"]["key"] = field
            parent["attr"]["value"] = value
            parent["attr"]["unit"] = self.unit_dict[col]
        # cond:attr
        elif field_nested_type == "cond-attr":
            parent["attr"][field_nested] = value
        # cond:data
        elif field_nested_type == "data":
            parent["data"].append(standardize_name(value))

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
            experiment_std_name = standardize_name(row["name"])
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
            material_std_name = standardize_name(row["material"])
            component_std_name = standardize_name(row["component"])
            parsed_mixture = {
                "index": index + 2,
                "component": component_std_name,
            }
            if material_std_name not in self.parsed:
                self.parsed[material_std_name] = []
            self.parsed[material_std_name].append(parsed_mixture)

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
                "index": index + 2,
                "name": row["name"],
            }
            data_std_name = standardize_name(row["name"])
            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row[col]
                if pd.isna(value):
                    continue

                # Handle foreign keys
                if field_type == "foreign_key":
                    parsed_datum[field] = standardize_name(value)

                # Populate parsed_datum dict
                if field_type == "base":
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
                parsed_column_name_obj = self.col_parsed[col]
                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys field
                if field_type == "foreign_keys":
                    parsed_file.update({field: value})

                # Populate parsed_file dict
                if field_type == "base":
                    parsed_file["base"][field] = value

            data_std_name = standardize_name(row["data"])
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
                "base": {},
                "iden": {},
                "prop": {},
                "cond": {},
                "index": index + 2,
                "name": row["name"],
            }
            material_std_name = standardize_name(row["name"])
            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle material base fields
                if field_type == "base":
                    parsed_material["base"][field] = value

                # Handle identity base fields
                if field_type == "iden":
                    parsed_material["iden"][field] = {
                        "key": field,
                        "value": value,
                    }

                # Handle properties
                if field_type == "prop":
                    self._parse_prop(col, 0, value, parsed_material)

                # Handle conditions
                if field_type == "cond":
                    self._parse_cond(col, 0, value, parsed_material)

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
                "prop": {},
                "cond": {},
                "index": index + 2,
                "name": row["name"],
            }
            experiment_std_name = standardize_name(row["experiment"])
            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys
                if field_type == "foreign_key":
                    parsed_process[field] = value

                # Handle base process fields
                if field_type == "base":
                    parsed_process["base"][field] = value

                # Handle properties
                if field_type == "prop":
                    self._parse_prop(col, 0, value, parsed_process)

                # Handle conditions
                if field_type == "cond":
                    self._parse_cond(col, 0, value, parsed_process)
            if experiment_std_name not in self.parsed:
                self.parsed[experiment_std_name] = []
            self.parsed[experiment_std_name].append(parsed_process)

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
                "dependent_process": standardize_name(row["dependent_process"]),
            }

            process_std_name = standardize_name(row["process"])
            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = []
            self.parsed[process_std_name].append(parsed_dependency)

        return self.parsed


class ProcessIngredientSheet(Sheet):
    """ProcessIngredient Excel sheet."""

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
                .join(str(self.df.loc[index, "ingredient"]))
            )
            self.df.loc[index, "process+ingredient"] = _value

    def parse(self):
        print(self.col_parsed)
        for index, row in self.df.iterrows():
            parsed_ingredient = {
                "base": {},
                "quan": {},
            }

            process_std_name = standardize_name(row["process"])
            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign key
                if field_type == "foreign_key":
                    parsed_ingredient[field] = value

                if field_type == "base":
                    parsed_ingredient["base"][field] = value

                # Handle process ingredient fields
                if field_type == "quan":
                    # Add quantity field with units
                    parsed_ingredient["quan"][field] = {
                        "key": field,
                        "value": value,
                        "unit": self.unit_dict[col],
                    }

            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = []
            self.parsed[process_std_name].append(parsed_ingredient)

        return self.parsed


class ProcessProductSheet(Sheet):
    """ProcessProduct Excel sheet."""

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
                .join(str(self.df.loc[index, "product"]))
            )
            self.df.loc[index, "process+product"] = _value

    def parse(self):
        for index, row in self.df.iterrows():
            parsed_product = {
                "index": index + 2,
                "product": standardize_name(row["product"]),
            }
            process_std_name = standardize_name(row["process"])

            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = []
            self.parsed[process_std_name].append(parsed_product)

        return self.parsed
