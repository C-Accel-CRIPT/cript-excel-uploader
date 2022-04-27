import pandas as pd

from src import configs
from src.errors import (
    UnsupportedColumnName,
    ColumnParseError,
)
from src.util import (
    standardize_name,
)
from src.parser import (
    ParsedColumnName,
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
            if self.sheet_name not in ["mixture component", "prerequisite process"]:
                print(f"Worksheet [{self.sheet_name}] not found in your excel file.")
        except Exception as e:
            print(
                f"There's an issue when we are trying to ingest your excel file. "
                f"Error info: {e.__str__()}"
            )

    def _data_preprocess(self):
        if self.df is None:
            return None

        # Drop Commented Columns
        for col in self.df.columns:
            if col[0] == "#":
                self.df = self.df.drop(col, axis=1)

        # Clean Column Name
        self.df.columns = [col.replace("*", "") for col in self.df.columns]

        # Drop NaN Columns:
        _subset = []
        for col in self.df.columns:
            if col not in configs.required_cols.get(self.sheet_name):
                _subset.append(col)
        nan_number = self.df.isna().sum()
        row_number = self.df.shape[0]
        for col in _subset:
            if nan_number.get(col) == row_number:
                self.df.drop(columns=col, inplace=True)

        self.cols = self.df.columns

        # Parse Column Name
        for col in self.cols:
            try:
                self.col_parsed[col] = parse_col_name(col)
            except ColumnParseError as e:
                exception = UnsupportedColumnName(
                    msg=e.__str__(),
                    col=col,
                    sheet=self.sheet_name,
                )
                self.errors.append(exception.__str__())
                self.col_parsed[col] = ParsedColumnName(is_valid=False)

        # Standardize and Categorize Field
        for col in self.col_parsed:
            parsed_col_name_obj = self.col_parsed[col]
            self._standardize_and_categorize_field(parsed_col_name_obj)

        # Create Unit Dict
        for col in self.cols:
            if 0 not in self.df.index or pd.isna(self.df.loc[0, col]):
                self.unit_dict[col] = None
            else:
                self.unit_dict[col] = self.df.loc[0, col].strip()

        # Drop Unit Row
        if 0 in self.df.index:
            self.df.drop(index=0, inplace=True)
        # Drop NaN Rows
        self.df.dropna(axis=0, how="all", inplace=True)

        # Remove Space
        for index, row in self.df.iterrows():
            for col in self.cols:
                value = row.get(col)
                if not pd.isna(value):
                    # Remove Space
                    if isinstance(value, str):
                        value = value.strip()
                        value = value.strip("\u202a")
                self.df.loc[index, col] = value

    def _create_foreign_key_dict(self):
        # Create Foreign Key Dict
        for col in self.foreign_keys:
            self.foreign_keys_dict[col] = {}
            for index, row in self.df.iterrows():
                value = row.get(col)
                _value = standardize_name(value)
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
            prev_field_type = field_type_list[i - 1] if i >= 1 else None
            found_tag = False

            if field is None:
                field_type_list.append(None)
                found_tag = True

            # Discussing with Dylan with this problem
            # Duplicated "volume" field for both quantity and condition
            # Cause errors in process ingredient sheet when categorizing
            if (
                not found_tag
                and field == "volume"
                and self.sheet_name == "process ingredient"
            ):
                field_type_list.append("quan")
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
                parsed_column_name_obj.is_valid = False
                break

    def _parse_prop(self, col, idx, start_index, value, parsed_object):
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
                "col": col,
                "idx": idx,
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
            self._parse_cond(col, idx, start_index + 1, value, parent)

    def _parse_cond(self, col, idx, start_index, value, parsed_object):
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
                "col": col,
                "idx": idx,
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


class ExperimentSheet(Sheet):
    """Experiment Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self._create_foreign_key_dict()
        self.parsed = {}

    def parse(self):
        if self.df is None:
            return self.parsed

        for index, row in self.df.iterrows():
            parsed_experiment = {
                "base": {},
                "index": index + 2,
                "name": row["name"],
            }
            experiment_std_name = standardize_name(row["name"])
            for col in self.cols:
                # Define value and field
                value = row.get(col)
                if value is None or pd.isna(value):
                    continue

                # Populate parsed_experiment dict
                if col in configs.base_cols["experiment"]:
                    parsed_experiment["base"][col] = value

            self.parsed[experiment_std_name] = parsed_experiment

        return self.parsed


class DataSheet(Sheet):
    """Data Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        if self.df is None:
            return self.parsed

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
                # Check whether current column name is valid
                if not parsed_column_name_obj.is_valid:
                    continue

                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row.get(col)
                if value is None or pd.isna(value):
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
        self._data_preprocess()
        self._create_foreign_key_dict()
        self.parsed = {}

    def parse(self):
        if self.df is None:
            return self.parsed

        for index, row in self.df.iterrows():
            parsed_file = {
                "base": {},
                "index": index + 2,
            }
            data_std_name = standardize_name(row["data"])

            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                # Check whether current column name is valid
                if not parsed_column_name_obj.is_valid:
                    continue

                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row.get(col)
                if value is None or pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys field
                if field_type == "foreign_key":
                    parsed_file[field] = standardize_name(value)

                # Populate parsed_file dict
                if field_type == "base":
                    parsed_file["base"][field] = value

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
        self._create_foreign_key_dict()
        self.parsed = {}

    def parse(self):
        if self.df is None:
            return self.parsed

        for index, row in self.df.iterrows():
            parsed_material = {
                "base": {},
                "iden": {},
                "prop": {},
                "index": index + 2,
                "name": row["name"],
            }
            material_std_name = standardize_name(row.get("name"))

            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                # Check whether current column name is valid
                if not parsed_column_name_obj.is_valid:
                    continue

                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row.get(col)
                if value is None or pd.isna(value):
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
                    self._parse_prop(col, index + 2, 0, value, parsed_material)

                # Handle conditions
                if field_type == "cond":
                    self._parse_cond(col, index + 2, 0, value, parsed_material)

            self.parsed[material_std_name] = parsed_material

        return self.parsed


class MixtureComponentSheet(Sheet):
    """MixtureComponent Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self._create_helper_cols()
        self._create_foreign_key_dict()
        self.parsed = {}

    def _create_helper_cols(self):
        if self.df is None:
            return None

        for index, row in self.df.iterrows():
            try:
                _value = (
                    "".join(self.df.loc[index, "process"])
                    .join("+")
                    .join(str(self.df.loc[index, "component"]))
                )
            except Exception:
                _value = None
            self.df.loc[index, "process+component"] = _value

    def parse(self):
        if self.df is None:
            return self.parsed

        for index, row in self.df.iterrows():
            material_std_name = standardize_name(row.get("material"))
            component_std_name = standardize_name(row.get("component"))
            parsed_mixture = {
                "component": component_std_name,
                "index": index + 2,
            }
            if material_std_name not in self.parsed:
                self.parsed[material_std_name] = []
            self.parsed[material_std_name].append(parsed_mixture)

        return self.parsed


class ProcessSheet(Sheet):
    """Process Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self._create_foreign_key_dict()
        self.parsed = {}

    def parse(self):
        if self.df is None:
            return self.parsed

        for index, row in self.df.iterrows():
            parsed_process = {
                "base": {},
                "prop": {},
                "cond": {},
                "index": index + 2,
                "name": row["name"],
            }
            experiment_std_name = standardize_name(row.get("experiment"))
            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                # Check whether current column name is valid
                if not parsed_column_name_obj.is_valid:
                    continue

                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row.get(col)
                if value is None or pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign keys
                if field_type == "foreign_key":
                    parsed_process[field] = standardize_name(value)

                # Handle base process fields
                if field_type == "base":
                    parsed_process["base"][field] = value

                # Handle properties
                if field_type == "prop":
                    self._parse_prop(col, index + 2, 0, value, parsed_process)

                # Handle conditions
                if field_type == "cond":
                    self._parse_cond(col, index + 2, 0, value, parsed_process)

            if experiment_std_name not in self.parsed:
                self.parsed[experiment_std_name] = []
            self.parsed[experiment_std_name].append(parsed_process)

        return self.parsed


class PrerequisiteProcessSheet(Sheet):
    """Prerequisite Excel sheet."""

    def __init__(self, path, sheet_name, param):
        super().__init__(path, sheet_name, param)

        self._read_file()
        self._data_preprocess()
        self._create_helper_cols()
        self._create_foreign_key_dict()
        self.parsed = {}

    def _create_helper_cols(self):
        if self.df is None:
            return None

        for index, row in self.df.iterrows():
            try:
                _value = (
                    "".join(self.df.loc[index, "process"])
                    .join("+")
                    .join(str(self.df.loc[index, "prerequisite_process"]))
                )
            except Exception:
                _value = None
            self.df.loc[index, "process+prerequisite_process"] = _value

    def parse(self):
        if self.df is None:
            return self.parsed

        for index, row in self.df.iterrows():
            parsed_dependency = {
                "prerequisite_process": standardize_name(row["prerequisite_process"]),
                "index": index + 2,
            }

            process_std_name = standardize_name(row.get("process"))
            if process_std_name is not None and process_std_name not in self.parsed:
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
        self._create_foreign_key_dict()
        self.parsed = {}

    def _create_helper_cols(self):
        if self.df is None:
            return None

        for index, row in self.df.iterrows():
            _value = (
                "".join(self.df.loc[index, "process"])
                .join("+")
                .join(str(self.df.loc[index, "ingredient"]))
            )
            self.df.loc[index, "process+ingredient"] = _value

    def parse(self):
        if self.df is None:
            return self.parsed

        for index, row in self.df.iterrows():
            parsed_ingredient = {
                "base": {},
                "quan": {},
                "index": index + 2,
            }

            process_std_name = standardize_name(row["process"])
            for col in self.cols:
                # Define value and field
                parsed_column_name_obj = self.col_parsed[col]
                # Check whether current column name is valid
                if not parsed_column_name_obj.is_valid:
                    continue

                field = parsed_column_name_obj.field_list[0]
                field_type = parsed_column_name_obj.field_type_list[0]
                value = row.get(col)
                if value is None or pd.isna(value):
                    continue

                if col in configs.list_fields[self.sheet_name]:
                    value = value.split(",")

                # Handle foreign key
                if field_type == "foreign_key":
                    parsed_ingredient[field] = standardize_name(value)

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
        self._create_foreign_key_dict()
        self.parsed = {}

    def _create_helper_cols(self):
        if self.df is None:
            return None

        for index, row in self.df.iterrows():
            try:
                _value = (
                    "".join(self.df.loc[index, "process"])
                    .join("+")
                    .join(str(self.df.loc[index, "product"]))
                )
            except Exception:
                _value = None
            self.df.loc[index, "process+product"] = _value

    def parse(self):
        if self.df is None:
            return self.df

        for index, row in self.df.iterrows():
            parsed_product = {
                "product": standardize_name(row["product"]),
                "index": index + 2,
            }
            process_std_name = standardize_name(row["process"])

            if process_std_name not in self.parsed:
                self.parsed[process_std_name] = []
            self.parsed[process_std_name].append(parsed_product)

        return self.parsed
