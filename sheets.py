import pandas as pd
import re

from params import params
from errors import (
    DataAssignmentError,
    UnsupportedFieldName,
    MissingRequiredField,
    UnsupportedUnitError,
)


class Sheet:
    """The base Sheet class."""

    def __init__(self, path, sheet_name):
        self.path = path
        self.sheet_name = sheet_name
        self.df = None

        self.cols = None
        self.required_cols = []
        self.either_or_cols = []
        self.not_null_cols = []
        self.list_fields = []
        self.col_lists_dict = {}

        self.unique_keys = []
        self.unique_keys_dict = {}
        self.foreign_keys = []
        self.foreign_keys_dict = {}

        self.unit_dict = {}

        self.errors = []
        self.has_error = False

    def _data_preprocess(self):
        try:
            self.df = pd.read_excel(self.path, sheet_name=self.sheet_name)
        except ValueError:
            print(f"Worksheet named [{self.sheet_name}] not found in the excel file.")

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

        # Standardize Field
        for col in self.col_lists_dict:
            col_list = self.col_lists_dict[col]
            field = col_list[-1]

            col_list[-1] = self._standardize_field(field)
            self.col_lists_dict[col] = col_list

        # Check Unit
        for col in self.cols:
            if pd.isna(self.df.loc[0, col]):
                self.unit_dict[col] = None
            else:
                self.unit_dict[col] = self.df.loc[0, col].strip()

        # Drop Unit Row
        self.df.drop(labels=0, axis=0, inplace=True)
        # Drop NaN Rows
        self.df.dropna(axis=0, how="all", inplace=True)

        # Remove Space, Convert id to Integer, Handle List Fields
        for index, row in self.df.iterrows():
            for col in self.cols:
                value = row[col]
                if pd.isna(value):
                    value = None
                else:
                    # Convert id to Integer
                    if col[-3:] == "_id":
                        value = int(value)
                    # Handle List Fields
                    if col in self.list_fields:
                        value = value.split(",")
                        value = [val.strip() for val in value]
                    # Remove Space
                    if isinstance(value, str):
                        value = value.strip()
                        value = value.strip("\u202a")
                self.df.loc[index, col] = value

        # Create Foreign Key Dict
        for col in self.foreign_keys:
            self.foreign_keys_dict[col] = {}
            for index, row in self.df.iterrows():
                value = row[col]
                _value = re.sub(r"[\s]+", "", str(value)).lower()
                self.foreign_keys_dict[col].update({_value: [value, index]})

    def _standardize_field(self, field):
        """
        Convert a field to the standardized version by searching the name in params.py (ex. temperature --> temp).

        :param field: field name
        :type field: str
        :raises: UnsupportedFieldName: input field name doesn't fit any acceptable one
        :return: standardized param name
        :rtype: str
        """
        # bad idea, will change later
        if field in self.required_cols or field == "data":
            return field
        for key in params:
            for param in params[key]:
                if field == param or field in params[key][param]["names"]:
                    return param

        exception = UnsupportedFieldName(field, self.sheet_name)
        self.errors.append(exception.__str__())

    def _check_required_cols(self):
        """
        Validate that all required columns are present.
        """
        for required_col in self.required_cols:
            if required_col not in self.cols:
                exception = MissingRequiredField(
                    field=required_col,
                    sheet=self.sheet_name,
                    is_either_or_cols=False,
                )
                self.errors.append(exception.__str__())

    def _check_either_or_cols(self):
        """
        Validate that at least one of the either/or columns are present.
        Validation passes when we find one either_or_col name in cols
        """
        exists = False
        if len(self.either_or_cols) == 0:
            exists = True

        for either_or_col in self.either_or_cols:
            if either_or_col in self.cols:
                exists = True
                break

        if not exists:
            exception = MissingRequiredField(
                field=self.either_or_cols,
                sheet=self.sheet_name,
                is_either_or_cols=True,
            )
            self.errors.append(exception.__str__())

    def _check_unit(self, supported_unit, input_unit, field, sheet_name):
        """
        Validate that the input unit is supported
        :param supported_unit: supported unit defined at params.py
        :type supported_unit: string
        :param input_unit: string, the unit defined by user
        :type input_unit: string
        :param field: string, corresponding field name
        :type field: string
        :param sheet_name: string, corresponding sheet name
        :type sheet_name: string
        :return boolean result whether the unit is valid.
        :rtype boolean
        :raise UnsupportedUnitError
        :raise MissingUnitError
        """
        if (
            supported_unit is not None
            and input_unit is not None
            and input_unit == supported_unit
        ):
            return True
        elif supported_unit is None and input_unit is None:
            return True
        else:
            exception = UnsupportedUnitError(
                input_unit=input_unit,
                supported_unit=supported_unit,
                field=field,
                sheet=self.sheet_name,
            )
            self.errors.append(exception.__str__())

    def _parse_data(self, col_list, parsed_object, value, prop_params):
        """
        Parse a data column and attach to it's appropriate parsed object.
        Currently used in material sheet and process sheet

        :param col_list: list generated by splitting column into separate fields (e.g., density:temp --> [density, temp])
        :type col_list: list
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        :param value: name of something in data sheet
        :type value: str
        :param prop_params property param template defined in params.py
        :type prop_params: dict
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
        if prev_field in prop_params:
            parent = parsed_object["prop"][prev_field]
        elif prev_field in params["cond"]:
            parent = parsed_object["cond"][prev_field]
        else:
            exception = DataAssignmentError(
                col_list=col_list,
                sheet=self.sheet_name,
                type=2,
            )
            self.errors.append(exception.__str__())
            return None

        parent["data"] = value

    def _parse_prop(
        self, col_list, field, value, parsed_object, prop_params, input_unit
    ):
        """
        Parse a property column with it's associated standard units and attributes.
        Currently used in material sheet and process sheet

        :param col_list: list generated by splitting column into separate fields (e.g., density:temp --> [density, temp])
        :type col_list: list
        :param field: specific field (property)
        :type field: str
        :param value: value of the reagent/material's property
        :type value: str
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        :param prop_params property param template defined in params.py
        :type prop_params: dict
        :param input_unit: unit of specific property defined by user
        :type input_unit: string
        """
        # Create property dict
        parsed_object["prop"].update(
            {
                field: {
                    "attr": {},
                    "data": {},
                }
            }
        )

        parsed_object["prop"][field].update({"value": value})

        # Add property units
        supported_unit = prop_params[field]["unit"]
        self._check_unit(supported_unit, input_unit, field, self.sheet_name)
        if input_unit:
            parsed_object["prop"][field].update({"unit": input_unit})

        # Add property attributes
        if field in params["prop"] and len(col_list) > 1:
            parsed_object["prop"][col_list[-2]]["attr"].update({field: value})

    def _parse_cond(self, col_list, field, value, parsed_object, input_unit):
        """
        Parse a condition column with it's associated standard units.
        Currently used in data sheet, material sheet and process sheet

        :param col_list: list generated by splitting column into separate fields (e.g., density:temp --> [density, temp])
        :type col_list: list
        :param field: specific field (condition)
        :type field: str
        :param value: value of the reagent/material's condition
        :type value: str
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        :param input_unit: unit of specific condition defined by user
        :type input_unit: string
        """
        # Set parent to the parsed object or a property
        if len(col_list) == 1:
            parent = parsed_object
        else:
            parent = parsed_object["prop"][col_list[-2]]

        # Create condition dict
        if "cond" not in parent:
            parent["cond"] = {}

        parent["cond"].update(
            {
                field: {
                    "data": {},
                }
            }
        )

        # Add condition value
        parent["cond"][field].update({"value": value})

        # Add condition units
        supported_unit = params["cond"][field]["unit"]
        self._check_unit(supported_unit, input_unit, field, self.sheet_name)
        if input_unit:
            parent["cond"][field].update({"unit": input_unit})


class ExperimentSheet(Sheet):
    """Experiment Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["name"]
        self.not_null_cols = ["name"]
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        # Validate required columns
        self._check_required_cols()

        for index, row in self.df.iterrows():
            parsed_experiment = {"index": index + 2}
            experiment_name = row["name"]
            for col in self.cols:
                value = row[col]

                # Populate parsed_experiment dict
                if col in params["experiment"]:
                    parsed_experiment[col] = value

            self.parsed[experiment_name] = parsed_experiment

        return self.parsed


class DataSheet(Sheet):
    """Data Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["experiment", "name", "data_type"]
        self.not_null_cols = ["experiment", "name", "data_type"]
        self.foreign_keys = ["experiment"]
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        # Validate required columns
        self._check_required_cols()

        for index, row in self.df.iterrows():
            parsed_datum = {"base": {}, "experiment": None, "index": index + 2}
            for col in self.cols:
                value = row[col]

                # Define field
                field = self.col_lists_dict[col][-1]

                # Handle foreign keys
                if field in self.foreign_keys:
                    parsed_datum[field] = value

                # Populate parsed_datum dict
                elif field in params["data"]:
                    parsed_datum["base"][field] = value

            self.parsed[row["name"]] = parsed_datum

        return self.parsed


class FileSheet(Sheet):
    """File Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["data", "path"]
        self.not_null_cols = ["data", "path"]
        self.foreign_keys = ["data"]
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        # Validate required columns
        self._check_required_cols()

        for index, row in self.df.iterrows():
            parsed_file = {
                "base": {},
                "data": None,
                "index": index,
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]

                # Define field
                field = self.col_lists_dict[col][-1]

                # Handle foreign keys field
                if field in self.foreign_keys:
                    parsed_file[field] = value

                # Populate parsed_datum dict
                elif field in params["file"]:
                    parsed_file["base"][field] = value

            data_name = row["data"]
            if data_name is not None:
                if data_name not in self.parsed:
                    self.parsed[data_name] = []
                self.parsed[data_name].append(parsed_file)

        return self.parsed


class MaterialSheet(Sheet):
    """Material Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["name"]
        self.not_null_cols = ["name"]
        self.list_fields = ["keywords", "names"]
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        # Validate required columns
        self._check_required_cols()

        for index, row in self.df.iterrows():
            parsed_material = {
                "base": {},
                "iden": {},
                "prop": {},
                "cond": {},
                "index": index + 2,
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]

                # Define field and col_list
                col_list = self.col_lists_dict[col]
                field = self.col_lists_dict[col][-1]

                # Handle list fields
                if field == "keywords":
                    parsed_material["base"][field] = row[field]
                    continue
                elif field == "names":
                    parsed_material["iden"]["names"] = row[field]
                    continue

                # Handle data
                if field == "data":
                    self._parse_data(
                        col_list,
                        parsed_material,
                        value,
                        params["material_prop"],
                    )
                    continue

                # Handle base material fields
                if field in params["material"]:
                    parsed_material["base"][field] = value

                # Handle material identity fields
                if field in params["identity"]:
                    parsed_material["iden"][field] = value

                # Handle properties
                if field in params["material_prop"]:
                    self._parse_prop(
                        col_list,
                        field,
                        value,
                        parsed_material,
                        params["material_prop"],
                        self.unit_dict[col],
                    )

                # Handle conditions
                if field in params["cond"]:
                    self._parse_cond(
                        col_list,
                        field,
                        value,
                        parsed_material,
                        self.unit_dict[col],
                    )

                self.parsed[row["name"]] = parsed_material

        return self.parsed


class ProcessSheet(Sheet):
    """Process Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["experiment", "name"]
        self.not_null_cols = ["experiment", "name"]
        self.foreign_keys = ["experiment"]
        self._data_preprocess()
        self.parsed = {}

    def parse(self):
        # Validate required columns
        self._check_required_cols()

        for index, row in self.df.iterrows():
            parsed_process = {
                "base": {},
                "index": index + 2,
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]

                # Define field
                field = self.col_lists_dict[col][-1]

                # Handle 'experiment' field
                if field in self.foreign_keys:
                    parsed_process[field] = value
                    continue

                # Handle lists
                if field == "keywords":
                    parsed_process["keywords"] = row["keywords"]
                    continue

                # Handle base process fields
                if field in params["process"]:
                    parsed_process["base"][field] = value

            self.parsed[row["name"]] = parsed_process

        return self.parsed


class StepSheet(Sheet):
    """Step Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["process", "step_id", "step_type"]
        self.not_null_cols = ["process", "step_id", "step_type", "keywords"]
        self.foreign_keys = ["process"]
        self._data_preprocess()
        self._create_helper_cols()
        self.parsed = {}

    def _create_helper_cols(self):
        for index, row in self.df.iterrows():
            _value = (
                self.df.loc[index, "process"] + ":" + str(self.df.loc[index, "step_id"])
            )
            self.df.loc[index, "process:step_id"] = _value

    def parse(self):

        # Validate required columns
        self._check_required_cols()

        for index, row in self.df.iterrows():
            parsed_step = {
                "base": {},
                "prop": {},
                "cond": {},
                "index": index + 2,
            }

            for col in self.cols:
                # Define and clean value
                value = row[col]

                # Define field
                col_list = self.col_lists_dict[col]
                field = self.col_lists_dict[col][-1]

                # Handle foreign key
                if field in self.foreign_keys:
                    parsed_step[field] = value
                    continue

                # Handle base step fields
                if field in params["step"]:
                    parsed_step["base"][field] = value

                # Handle properties
                elif field in params["step_prop"]:
                    self._parse_prop(
                        col_list,
                        field,
                        value,
                        parsed_step,
                        params["step_prop"],
                        self.unit_dict[col],
                    )

                # Handle conditions
                elif field in params["cond"]:
                    self._parse_cond(
                        col_list,
                        field,
                        value,
                        parsed_step,
                        self.unit_dict[col],
                    )

            if row["process"] not in self.parsed:
                self.parsed[row["process"]] = {}
            self.parsed[row["process"]][row["step_id"]] = parsed_step

        return self.parsed


class StepIngredientSheet(Sheet):
    """StepIngredient Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["process", "step_id", "keyword", "ingredient"]
        self.either_or_cols = ["mole", "mass", "volume"]
        self.not_null_cols = ["process", "step_id", "keyword", "ingredient"]
        self.foreign_key = ["process", "step_id", "ingredient"]
        self._data_preprocess()
        self._create_helper_cols()
        self.parsed = {}

    def _create_helper_cols(self):
        for index, row in self.df.iterrows():
            _value = (
                self.df.loc[index, "process"] + ":" + str(self.df.loc[index, "step_id"])
            )
            self.df.loc[index, "process:step_id"] = _value

            self.df.loc[index, "ingredient-material"] = None
            self.df.loc[index, "ingredient-step"] = None
            _list = self.df.loc[index, "ingredient"].split(":")
            # Data assign error check
            if len(_list) == 1:
                self.df.loc[index, "ingredient-material"] = _list[0]
            if len(_list) == 2:
                self.df.loc[index, "ingredient-step"] = _list[0] + ":" + _list[1]

    def parse(self):
        # Validate required columns
        self._check_required_cols()

        # Validate either/or columns
        self._check_either_or_cols()

        for index, row in self.df.iterrows():
            parsed_ingredient = {
                "quantity": {},
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]

                # Define field
                field = self.col_lists_dict[col][-1]

                # Handle foreign key
                if field in self.foreign_keys:
                    parsed_ingredient[field] = value

                # Handle process ingredient fields
                if field in params["step_reagent_and_product"]:
                    supported_unit = params["step_reagent_and_product"][field]["unit"]
                    input_unit = self.unit_dict.get(col)
                    self._check_unit(
                        supported_unit,
                        input_unit,
                        field,
                        self.sheet_name,
                    )
                    if input_unit:
                        # Skip if a quantity field has already been parsed
                        if len(parsed_ingredient["quantity"]) > 0:
                            continue

                        # Add quantity field with units
                        parsed_ingredient["quantity"][field] = {
                            "value": value,
                            "unit": input_unit,
                        }
                    else:
                        parsed_ingredient[field] = value

            if row["process"] not in self.parsed:
                self.parsed[row["process"]] = {}
            if row["step_id"] not in self.parsed[row["process"]]:
                self.parsed[row["process"]][row["step_id"]] = []
            self.parsed[row["process"]][row["step_id"]].append(parsed_ingredient)

        return self.parsed


class StepProductSheet(Sheet):
    """StepProduct Excel sheet."""

    def __init__(self, path, sheet_name):
        super().__init__(path, sheet_name)

        self.required_cols = ["process", "step_id", "keyword", "product"]
        self.not_null_cols = ["process", "step_id", "keyword", "product"]
        self.foreign_keys = ["process", "step_id", "product"]
        self._data_preprocess()
        self._create_helper_cols()
        self.parsed = {}

    def _create_helper_cols(self):
        for index, row in self.df.iterrows():
            _value = (
                self.df.loc[index, "process"] + ":" + str(self.df.loc[index, "step_id"])
            )
            self.df.loc[index, "process:step_id"] = _value

    def parse(self):
        # Validate required columns
        self._check_required_cols()

        for index, row in self.df.iterrows():
            parsed_product = {}
            for col in self.cols:
                # Define and clean value
                value = row[col]

                # Define field
                field = self.col_lists_dict[col][-1]

                if field in self.foreign_keys:
                    parsed_product[field] = value

                # Handle process ingredient fields
                if field in params["step_reagent_and_product"]:
                    parsed_product[field] = value

            if row["process"] not in self.parsed:
                self.parsed[row["process"]] = {}
            if row["step_id"] not in self.parsed[row["process"]]:
                self.parsed[row["process"]][row["step_id"]] = []
            self.parsed[row["process"]][row["step_id"]].append(parsed_product)

        return self.parsed
