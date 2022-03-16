class DataAssignmentError(Exception):
    def __init__(self, col_list, sheet, type):
        self.sheet = sheet
        self.col_list = col_list
        self.field = None
        if len(col_list) == 1:
            self.field = col_list[-1]
        elif len(col_list) == 2:
            self.field = col_list[-2] + ":" + col_list[-1]
        self.type = type

    def __str__(self):
        if type == 1:
            return (
                f"DataAssignmentError: "
                f"Sheet [{self.sheet}], "
                f"Field [{self.field}], "
                f"You need to apply [{self.col_list[0]}] to something. "
                f"Eg. (property):data, (condition):data"
            )
        elif type == 2:
            return {
                f"DataAssignmentError: "
                f"Sheet [{self.sheet}], "
                f"Field [{self.field}], "
                f"{self.col_list[-2]} is neither a property "
                f"nor a condition of {self.col_list[-1]}."
            }


class UnsupportedFieldName(Exception):
    def __init__(self, field, sheet):
        self.sheet = sheet
        self.field = field

    def __str__(self):
        return (
            f"UnsupportedFieldName: "
            f"Sheet [{self.sheet}], "
            f"Field [{self.field}], "
            f"Input field is not supported."
        )


class UnsupportedValue(Exception):
    def __init__(self, value, field):
        self.value = value
        self.field = field

    def __str__(self):
        return f"'{self.value}' is not a supported value for '{self.field}'"


class ValueDoesNotExist(Exception):
    def __init__(self, value, index, field, sheet, sheet_to_check, field_to_check):
        self.value = value
        self.index = index
        self.field = field
        self.sheet = sheet
        self.sheet_to_check = sheet_to_check
        self.field_to_check = field_to_check

        self.field = self.field.strip("#")
        self.field = self.field.split("-")[0]

    def __str__(self):
        return (
            f"ValueDoesNotExist: "
            f"Sheet [{self.sheet}], "
            f"Field [{self.field}], "
            f"Index [{self.index}], "
            f"Value [{self.value}] does not exist "
            f"in the [{self.field_to_check}] field "
            f"of [{self.sheet_to_check}] sheet."
        )


class DuplicatedValueError(Exception):
    def __init__(self, value1, index1, value2, index2, field, sheet):
        self.value1 = value1
        self.index1 = index1
        self.value2 = value2
        self.index2 = index2
        self.field = field
        self.sheet = sheet

    def __str__(self):
        return (
            f"DuplicatedValueError: "
            f"Sheet [{self.sheet}], "
            f"Field [{self.field}], "
            f"Index [{self.index1}], "
            f"Value [{self.value1}] is duplicated with"
            f"value [{self.value2}] at index [{self.index2}]. "
            f"Every value should be unique in this field."
        )


class NullValueError(Exception):
    def __init__(self, index, field, sheet):
        self.index = index
        self.field = field
        self.sheet = sheet

    def __str__(self):
        return (
            f"NullValueError: "
            f"Sheet [{self.sheet}], "
            f"Field [{self.field}], "
            f"Index [{self.index}], "
            f"Null value is not allowed for this field."
        )


class MissingRequiredField(Exception):
    def __init__(self, field, sheet, is_either_or_cols=False):
        self.field = field
        self.sheet = sheet
        self.is_either_or_cols = is_either_or_cols

    def __str__(self):
        if not self.is_either_or_cols:
            return (
                f"MissingRequiredField: "
                f"Sheet [{self.sheet}], "
                f"Field [{self.field}], "
                f"Please add the missing required field to the sheet."
            )
        else:
            return (
                f"MissingRequiredFieldError: "
                f"Sheet [{self.sheet}], "
                f"Field {self.field}, "
                f"Must include at least one of the fields from the list."
            )


class UnsupportedUnitError(Exception):
    def __init__(self, input_unit, supported_unit, field, sheet):
        self.input_unit = input_unit
        self.supported_unit = supported_unit
        self.field = field
        self.sheet = sheet

    def __str__(self):
        return (
            f"UnsupportedUnitName: "
            f"Sheet [{self.sheet}], "
            f"Field [{self.field}], "
            f"Unit [{self.input_unit}] "
            f"Input unit is not supported. "
            f"Supported unit: [{self.supported_unit}]."
        )


class MissingUnitError(Exception):
    def __init__(self, field, sheet, message=""):
        self.field = field
        self.sheet = sheet
        self.message = message

    def __str__(self):
        return (
            f"Unit for '{self.field}' is required column in the '{self.sheet}' Excel sheet."
            + self.message
        )


class GroupRelatedError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"
