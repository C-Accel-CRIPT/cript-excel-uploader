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

        # Standardize and Categorize Field
        for col in self.col_parsed:
            parsed_col_name_obj = self.col_parsed[col]
            field, field_type = self._standardize_and_categorize_field(
                parsed_col_name_obj.field,
                parsed_col_name_obj.origin_col,
            )
            field_nested, field_nested_type = self._standardize_and_categorize_field(
                parsed_col_name_obj.field_nested,
                parsed_col_name_obj.origin_col,
                field_type,
            )
            parsed_col_name_obj.field = field
            parsed_col_name_obj.field_type = field_type
            parsed_col_name_obj.field_nested = field_nested
            parsed_col_name_obj.field_nested_type = field_nested_type

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

    def _standardize_and_categorize_field(
        self, field, origin_col, prev_field_type=None
    ):
        """
        Convert a field to the standardized version

        :return: standardized param name
        :rtype: str
        """
        if field is None:
            return None, None

        # Foreign keys
        if field in self.foreign_keys:
            return field, "foreign_key"

        # Base cols
        for base_node in configs.base_nodes.get(self.sheet_name):
            if field in configs.base_cols.get(base_node):
                return field, "base"

        # Data keys
        if field == "data":
            return field, "data"

        # Identifier Keys
        iden_key = "material-identifier-key"
        for iden in self.param[iden_key]:
            if field == iden["name"]:
                return iden["name"], "iden"

        # Property Keys
        prop_key = configs.sheet_name_to_prop_key.get(self.sheet_name)
        if prop_key is not None:
            for prop in self.param[prop_key]:
                if field == prop["name"]:
                    return prop["name"], "prop"

        # Condition Keys
        cond_key = "condition-key"
        for cond in self.param[cond_key]:
            if field == cond["name"]:
                return cond["name"], "cond"

        quan_key = "quantity-key"
        for quan in self.param[quan_key]:
            if field == quan["name"]:
                return quan["name"], "quan"

        if prev_field_type == "prop":
            for prop_attr in configs.base_cols["property"]:
                if field == prop_attr:
                    return field, "prop-attr"

        if prev_field_type == "cond":
            for cond_attr in configs.base_cols["condition"]:
                if field == cond_attr:
                    return field, "cond-attr"

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
            parent["data"].append(value)
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
            parent["attr"]["unit"] = field
        # cond:attr
        elif field_nested_type == "cond-attr":
            parent["attr"][field_nested] = value
        # cond:data
        elif field_nested_type == "data":
            parent["data"].append(value)

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
                "experiment": None,
                "index": index + 2,
                "name": row["name"],
            }
            data_std_name = standardize_name(row["name"])
            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                field = parsed_column_name_obj.field_list[0]
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
                parsed_column_name_obj = self.col_parsed[col]
                field = parsed_column_name_obj.field_list[0]
                value = row[col]
                if pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys field
                if field in self.foreign_keys:
                    parsed_file.update({field: value})

                # Populate parsed_file dict
                if col in configs.base_cols.get("file"):
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
                    parsed_material["iden"][field] = value

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
                if field in self.foreign_keys:
                    parsed_process[field] = value

                # Handle base process fields
                if col in configs.base_cols.get("process"):
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
                "dependent_process": row["dependent_processes"],
            }

            process_std_name = standardize_name(row["process"])
            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = {}
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
        for index, row in self.df.iterrows():
            parsed_ingredient = {
                "base": {},
                "quantity": {},
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
                if field in self.foreign_keys:
                    parsed_ingredient[field] = value

                if field_type == "base":
                    parsed_ingredient["base"][field] = value

                # Handle process ingredient fields
                if field_type == "quantity":
                    # Add quantity field with units
                    parsed_ingredient["quantity"][field] = {
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
