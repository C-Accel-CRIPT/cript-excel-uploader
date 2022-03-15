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
    def __init__(self, value, sheet):
        self.value = value
        self.sheet = sheet

    def __str__(self):
        return f"'{self.value}' does not exist in the {self.sheet} Excel sheet."


class MissingRequiredField(Exception):
    def __init__(self, field, sheet, is_either_or_cols=False):
        self.field = field
        self.sheet = sheet
        self.is_either_or_cols = is_either_or_cols

    def __str__(self):
        if not self.is_either_or_cols:
            return (
                f"MissingRequiredFieldError: "
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


# Add it to validator
# class MissingRequiredFieldValue(Exception):
#     def __init__(self, index, field, sheet, is_either_or_cols=False):
#         self.field = field
#         self.sheet = sheet
#         self.is_either_or_cols = is_either_or_cols
#
#     def __str__(self):
#         if not self.is_either_or_cols:
#             return (
#                 f"MissingRequiredFieldError: "
#                 f"Sheet [{self.sheet}], "
#                 f"Field [{self.field}], "
#                 f"Please add the missing required field to the sheet."
#             )
#         else:
#             return (
#                 f"MissingRequiredFieldError: "
#                 f"Sheet [{self.sheet}], "
#                 f"Field {self.field}, "
#                 f"Must include at least one of the fields from the list."
#             )


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
