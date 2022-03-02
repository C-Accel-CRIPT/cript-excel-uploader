import numpy
import pandas as pd

from params import params
from errors import (
    DataAssignmentError,
    UnsupportedFieldName,
    UnsupportedValue,
    ValueDoesNotExist,
    MissingRequiredFieldError,
    UnsupportedUnitError,
    MissingUnitError,
)


class Sheet:
    """The base Sheet class."""

    def __init__(self, path, sheet_name):
        self.path = path
        self.sheet_name = sheet_name

        self.df = pd.read_excel(path, sheet_name=sheet_name)
        self.df.dropna(how="all", inplace=True)

        self.cols = self.df.columns

    def _skip_col(self, col, val):
        """
        Check if a column should be skipped.

        :param col: column name (eg.*name)
        :type col: str
        :param val: specific value belongs to the column (eg.Exp1)
        :type val: str
        :return: boolean result whether the col should be skipped
        :rtype: bool
        """
        # Check if val empty
        if pd.isna(val):
            return True

        # Check if col starts with '#'
        if col[0] == "#":
            return True

        return False

    def _standardize_field(self, field):
        """
        Convert a field to the standardized version by searching the name in params.py (ex. temperature --> temp).

        :param field: field name
        :type field: str
        :raises: UnsupportedFieldName: input field name doesn't fit any acceptable one
        :return: standardized param name
        :rtype: str
        """
        for key in params:
            for param in params[key]:
                if field == param or field in params[key][param]["names"]:
                    return param

        raise UnsupportedFieldName(field)

    def _check_required_cols(self, required_cols, cols, sheet_name):
        """
        Validate that all required columns are present.

        :param required_cols: a list contains required column names
        :type required_cols: list
        :param cols: a list contains all the column names in a sheet
        :type cols: list
        :param sheet_name: sheet_name
        :type sheet_name: str
        :raises: MissingRequiredFieldError: Missing required column in the excel template
        """
        for required_col in required_cols:
            if required_col in cols:
                continue

            required_col = required_col.replace("*", "")
            raise MissingRequiredFieldError(required_col, sheet_name)

    def _check_either_or_cols(self, either_or_cols, cols, sheet_name, message=""):
        """
        Validate that at least one of the either/or columns are present.
        Validation passes when we find one either_or_col name in cols

        :param either_or_cols: a list contains either_or column names
        :type either_or_cols: list
        :param cols list list, a list contains all the column names in a sheet
        :param sheet_name string, sheet_name
        :param message string, A message tells the user what's either_or column
        :raises: MissingRequiredFieldError: Missing either_or column in the excel template
        """
        exists = False
        for either_or_col in either_or_cols:
            if either_or_col in cols:
                exists = True
                break

        if exists == False:
            raise MissingRequiredFieldError("quantity", sheet_name, message)

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
        if supported_unit is not None and input_unit is not None:
            if input_unit == supported_unit:
                return True
            else:
                raise UnsupportedUnitError(input_unit, field)
        elif supported_unit is not None and input_unit is None:
            raise MissingUnitError(field, sheet_name)
        elif supported_unit is None and input_unit is not None:
            raise UnsupportedUnitError(input_unit, field)
        else:
            return True

    def _parse_data(self, col_list, parsed_object, value, parsed_data, prop_params):
        """
        Parse a data column and attach to it's appropriate parsed object.
        Currently used in material sheet and process sheet

        :param col_list: list generated by splitting column into separate fields (e.g., density:temp --> [density, temp])
        :type col_list: list
        :param parsed_object: the dict object the data is being applied to
        :type parsed_object: dict
        :param value: name of something in data sheet
        :type value: str
        :param parsed_data: data extracted from excel sheet with name as keys, defined in DataSheet class
        :type parsed_data: dict
        :param prop_params property param template defined in params.py
        :type prop_params: dict
        :raises: ValueDoesNotExist: can't find the data of the material from data sheet according to input name.
        :raises: DataAssignmentError: data is not applied to a prop or cond (e.g., molar_mass:data)
        """
        # Check if data name exists in the data sheet
        if value not in parsed_data:
            raise ValueDoesNotExist(value, "data")

        # Ensure the data is being applied to something
        if len(col_list) == 1:
            raise DataAssignmentError

        # Check if data should be applied to a property or condition
        prev_field = col_list[-2]
        if prev_field in prop_params:
            parent = parsed_object["prop"][prev_field]
        elif prev_field in params["cond"]:
            parent = parsed_object["cond"][prev_field]
        else:
            raise DataAssignmentError

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
        if "cond" in parent:
            parent["cond"].update(
                {
                    field: {
                        "data": {},
                    }
                }
            )
        else:
            parent["cond"] = {
                field: {
                    "data": {},
                }
            }

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
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self):
        # Validate required columns
        required_cols = ["*name"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_experiment = {}
            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col
                col = col.replace("*", "")

                # Standardize col field
                col = self._standardize_field(col)

                # Populate parsed_experiment dict
                if col in params["experiment"]:
                    parsed_experiment[col] = value

            self.parsed[row["*name"].strip()] = parsed_experiment

        return self.parsed


class DataSheet(Sheet):
    """Data Excel sheet."""

    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_experiments):
        # Validate required columns
        required_cols = ["*experiment", "*name", "*data_type"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_datum = {
                "base": {},
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col and create col_list
                col = col.replace("*", "")
                col_list = col.split(":")

                # Define field
                field = col_list[-1]

                # Handle 'experiment' field
                if field == "experiment":
                    if value in parsed_experiments:
                        parsed_datum["expt"] = value
                    else:
                        raise ValueDoesNotExist(value, "experiment")
                    continue

                # Standardize field
                field = self._standardize_field(field)

                # Populate parsed_datum dict
                if field in params["data"]:
                    parsed_datum["base"][field] = value

            self.parsed[row["*name"].strip()] = parsed_datum

        return self.parsed


class FileSheet(Sheet):
    """File Excel sheet."""

    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_data):
        # Validate required columns
        required_cols = ["*data", "*path"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_datum = {
                "base": {},
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col and create col_list
                col = col.replace("*", "")
                col_list = col.split(":")

                # Define field
                field = col_list[-1]

                # Handle 'data' field
                if field == "data":
                    if value in parsed_data:
                        parsed_datum["data"] = value
                    else:
                        raise ValueDoesNotExist(value, "data")
                    continue

                # Standardize field
                field = self._standardize_field(field)

                # Populate parsed_datum dict
                if field in params["file"]:
                    parsed_datum["base"][field] = value

            if row["*data"] in self.parsed:
                self.parsed[row["*data"]].append(parsed_datum)
            else:
                self.parsed[row["*data"]] = [parsed_datum]

        return self.parsed


class MaterialSheet(Sheet):
    """Material Excel sheet."""

    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_data):
        unit = {}

        # Validate required columns
        required_cols = ["*name"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_material = {
                "base": {},
                "iden": {},
                "prop": {},
                "cond": {},
            }

            for col in self.cols:
                if index == 0:
                    if pd.isna(row[col]):
                        unit[col] = None
                    else:
                        unit[col] = row[col]
                else:
                    # Define and clean value
                    value = row[col]
                    if isinstance(value, str):
                        value = value.strip()

                    # Check if col should be skipped
                    if self._skip_col(col, value) == True:
                        continue

                    # Clean col and create col_list
                    col = col.replace("*", "")
                    col_list = col.split(":")

                    # Define field
                    field = col_list[-1]

                    # Handle list fields
                    if field == "keywords":
                        parsed_material["base"][field] = row[field].split(",")
                        continue
                    elif field == "names":
                        parsed_material["iden"]["names"] = row["names"].split(",")
                        continue

                    # Handle data
                    if field == "data":
                        self._parse_data(
                            col_list,
                            parsed_material,
                            value,
                            parsed_data,
                            params["material_prop"],
                        )
                        continue

                    # Standardize field
                    field = self._standardize_field(field)

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
                            unit[col],
                        )

                    # Handle conditions
                    if field in params["cond"]:
                        self._parse_cond(
                            col_list,
                            field,
                            value,
                            parsed_material,
                            unit[col],
                        )

                    self.parsed[row["*name"].strip()] = parsed_material

        return self.parsed


class ProcessSheet(Sheet):
    """Process Excel sheet."""

    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_experiments):
        # Validate required columns
        required_cols = ["*experiment", "*name"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_process = {
                "base": {},
            }
            for col in self.cols:
                # Define and clean value
                value = row[col]
                if isinstance(value, str):
                    value = value.strip()

                # Check if col should be skipped
                if self._skip_col(col, value) == True:
                    continue

                # Clean col and create col_list
                col = col.replace("*", "")
                col_list = col.split(":")

                # Define field
                field = col_list[-1]

                # Handle 'experiment' field
                if field == "experiment":
                    if value in parsed_experiments:
                        parsed_process["expt"] = value
                    continue

                # Handle lists
                if field == "keywords":
                    parsed_process["keywords"] = row["keywords"].split(",")
                    continue

                # Sandardize field
                field = self._standardize_field(field)

                # Handle base process fields
                if field in params["process"]:
                    parsed_process["base"][field] = value

            self.parsed[row["*name"].strip()] = parsed_process

        return self.parsed


class StepSheet(Sheet):
    """Step Excel sheet."""

    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(self, parsed_data, parsed_process):
        unit = {}

        # Validate required columns
        required_cols = ["*process", "*step_id", "*step_type"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_step = {
                "base": {},
                "prop": {},
                "cond": {},
            }

            for col in self.cols:
                if index == 0:
                    if pd.isna(row[col]):
                        unit[col] = None
                    else:
                        unit[col] = row[col]
                else:
                    # Define and clean value
                    value = row[col]
                    if isinstance(value, str):
                        value = value.strip()

                    # Check if col should be skipped
                    if self._skip_col(col, value) == True:
                        continue

                    # Clean col and create col_list
                    col = col.replace("*", "")
                    col_list = col.split(":")

                    # Define field
                    field = col_list[-1]

                    # Handle process
                    if field == "process":
                        if value in parsed_process:
                            parsed_step["process"] = value
                        continue

                    # Standardize field
                    field = self._standardize_field(field)

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
                            unit[col],
                        )

                    # Handle conditions
                    elif field in params["cond"]:
                        self._parse_cond(
                            col_list,
                            field,
                            value,
                            parsed_step,
                            unit[col],
                        )

                    if row["*process"].strip() not in self.parsed:
                        self.parsed[row["*process"].strip()] = {}
                    self.parsed[row["*process"].strip()][row["*step_id"]] = parsed_step

        return self.parsed


class StepIngredientSheet(Sheet):
    """StepIngredient Excel sheet."""

    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(
        self,
        parsed_materials,
        parsed_process,
        parsed_steps,
    ):
        unit = {}
        # Validate required columns
        required_cols = ["*process", "*step_id", "*keyword", "*ingredient"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        # Validate either/or columns
        either_or_cols = ["mole", "mass", "volume"]
        message = " Options: mole, mass, and/or volume."
        self._check_either_or_cols(either_or_cols, self.cols, self.sheet_name, message)

        for index, row in self.df.iterrows():
            parsed_ingredient = {
                "quantity": {},
            }
            for col in self.cols:
                if index == 0:
                    if pd.isna(row[col]):
                        unit[col] = None
                    else:
                        unit[col] = row[col]
                else:
                    # Define and clean value
                    value = row[col]
                    if isinstance(value, str):
                        value = value.strip()

                    # Check if col should be skipped
                    if self._skip_col(col, value) == True:
                        continue

                    # Clean col and create col_list
                    col = col.replace("*", "")
                    col_list = col.split(":")

                    # Define field
                    field = col_list[-1]

                    # Handle process field
                    if field == "process":
                        if value not in parsed_process:
                            raise ValueDoesNotExist(value, "process")
                        continue

                    # Handle step_id field
                    if field == "step_id":
                        if value not in parsed_steps[row["*process"]]:
                            raise ValueDoesNotExist(value, "step_id")
                        continue

                    # Handle ingredient field
                    if field == "ingredient":
                        if value not in parsed_materials:
                            raise ValueDoesNotExist(value, "ingredient")
                        continue

                    # Handle process ingredient fields
                    if field in params["step_reagent_and_product"]:
                        supported_unit = params["step_reagent_and_product"][field][
                            "unit"
                        ]
                        input_unit = None
                        if col in unit:
                            input_unit = unit[col]
                        self._check_unit(
                            supported_unit, input_unit, field, self.sheet_name
                        )
                        if input_unit:
                            # Skip if a quantity field has already been parsed
                            if len(parsed_ingredient["quantity"]) > 0:
                                continue

                            # Add quantity field with units
                            parsed_ingredient["quantity"][field] = {"value": value}
                            parsed_ingredient["quantity"][field].update(
                                {"unit": input_unit}
                            )
                        else:
                            parsed_ingredient[field] = value
                    else:
                        raise UnsupportedFieldName(field)

                    if row["*step_id"] in self.parsed:
                        self.parsed[row["*step_id"]].append(parsed_ingredient)
                    else:
                        self.parsed[row["*step_id"]] = [parsed_ingredient]

        return self.parsed


class StepProductSheet(Sheet):
    """StepProduct Excel sheet."""

    def __init__(self, path, sheet_name):
        self.parsed = {}

        super().__init__(path, sheet_name)

    def parse(
        self,
        parsed_materials,
        parsed_process,
        parsed_steps,
    ):
        unit = {}
        # Validate required columns
        required_cols = ["*process", "*step_id", "*keyword", "*product"]
        self._check_required_cols(required_cols, self.cols, self.sheet_name)

        for index, row in self.df.iterrows():
            parsed_product = {
                "quantity": {},
            }
            for col in self.cols:
                if index == 0:
                    if pd.isna(row[col]):
                        unit[col] = None
                    else:
                        unit[col] = row[col]
                else:
                    # Define and clean value
                    value = row[col]
                    if isinstance(value, str):
                        value = value.strip()

                    # Check if col should be skipped
                    if self._skip_col(col, value) == True:
                        continue

                    # Clean col and create col_list
                    col = col.replace("*", "")
                    col_list = col.split(":")

                    # Define field
                    field = col_list[-1]

                    # Handle process field
                    if field == "process":
                        if value not in parsed_process:
                            raise ValueDoesNotExist(value, "process")
                        continue

                    # Handle step_id field
                    if field == "step_id":
                        if value not in parsed_steps[row["*process"]]:
                            raise ValueDoesNotExist(value, "step_id")
                        continue

                    # Handle ingredient field
                    if field == "product":
                        if value not in parsed_materials:
                            raise ValueDoesNotExist(value, "product")
                        continue

                    # Handle process ingredient fields
                    if field in params["step_reagent_and_product"]:
                        supported_unit = params["step_reagent_and_product"][field][
                            "unit"
                        ]
                        input_unit = None
                        if col in unit:
                            input_unit = unit[col]
                        self._check_unit(
                            supported_unit, input_unit, field, self.sheet_name
                        )
                        if input_unit:
                            # Skip if a quantity field has already been parsed
                            if len(parsed_product["quantity"]) > 0:
                                continue

                            # Add quantity field with units
                            parsed_product["quantity"][field] = {"value": value}
                            parsed_product["quantity"][field].update(
                                {"unit": input_unit}
                            )
                        else:
                            parsed_product[field] = value
                    else:
                        raise UnsupportedFieldName(field)

                    if row["*step_id"] in self.parsed:
                        self.parsed[row["*step_id"]].append(parsed_product)
                    else:
                        self.parsed[row["*step_id"]] = [parsed_product]

        return self.parsed
