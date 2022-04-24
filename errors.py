class UnsupportedColumnName(Exception):
    def __init__(self, col, sheet, field=None, message=None):
        self.sheet = sheet
        self.col = col
        self.message = message
        self.field = field

    def __str__(self):
        if self.message:
            return (
                f"UnsupportedColumnName: "
                f"Sheet [{self.sheet}], "
                f"Column [{self.col}], "
                f"Input Column name is not supported."
                f"Message: {self.message}"
            )
        elif self.field:
            return (
                f"UnsupportedColumnName: "
                f"Sheet [{self.sheet}], "
                f"Column [{self.col}],"
                f"Field [{self.field}], "
                f"Input field in the column name is not supported."
            )
        else:
            return (
                f"UnsupportedFieldName: "
                f"Sheet [{self.sheet}], "
                f"Column [{self.col}], "
                f"Input Column Name is not supported."
            )


class UnsupportedValue(Exception):
    def __init__(self, value, col):
        self.value = value
        self.col = col

    def __str__(self):
        return f"'{self.value}' is not a supported value for '{self.col}'"


class ValueDoesNotExist(Exception):
    def __init__(self, value, index, col, sheet, sheet_to_check, col_to_check):
        self.value = value
        self.index = index
        self.col = col
        self.sheet = sheet
        self.sheet_to_check = sheet_to_check
        self.col_to_check = col_to_check

        self.col = self.col.strip("#")
        self.col = self.col.split("-")[0]

    def __str__(self):
        return (
            f"ValueDoesNotExist: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.index}], "
            f"Value [{self.value}] does not exist "
            f"in the [{self.col_to_check}] column "
            f"of [{self.sheet_to_check}] sheet."
        )


class DuplicatedValueError(Exception):
    def __init__(self, value1, index1, value2, index2, col, sheet):
        self.value1 = value1
        self.index1 = index1
        self.value2 = value2
        self.index2 = index2
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"DuplicatedValueError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.index1}], "
            f"Value [{self.value1}] is duplicated with"
            f"value [{self.value2}] at index [{self.index2}]. "
            f"Every value should be unique in this column."
        )


class NullValueError(Exception):
    def __init__(self, index, col, sheet):
        self.index = index
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"NullValueError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.index}], "
            f"Null value is not allowed for this column."
        )


class MissingRequiredColumn(Exception):
    def __init__(self, col, sheet, is_either_or_cols=False):
        self.col = col
        self.sheet = sheet
        self.is_either_or_cols = is_either_or_cols

    def __str__(self):
        if not self.is_either_or_cols:
            return (
                f"MissingRequiredColumn: "
                f"Sheet [{self.sheet}], "
                f"Column [{self.col}], "
                f"Please add the missing required column to the sheet."
            )
        else:
            return (
                f"MissingRequiredColumnError: "
                f"Sheet [{self.sheet}], "
                f"Column {self.col}, "
                f"Must include at least one of the columns from the list."
            )


class InvalidIdentifierError(Exception):
    def __init__(self, msg, idx, col, sheet):
        self.msg = msg
        self.idx = idx
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"InvalidIdentifierError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx}], "
            f"Error Message: {self.msg}"
        )


class InvalidPropertyError(Exception):
    def __init__(self, msg, idx, col, sheet):
        self.msg = msg
        self.idx = idx
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"InvalidPropertyError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx}], "
            f"Error Message: {self.msg}"
        )


class InvalidConditionError(Exception):
    def __init__(self, msg, idx, col, sheet):
        self.msg = msg
        self.idx = idx
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"InvalidConditionError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx}], "
            f"Error Message: {self.msg}"
        )


class InvalidQuantityError(Exception):
    def __init__(self, msg, idx, col, sheet):
        self.msg = msg
        self.idx = idx
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"InvalidQuantityError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx}], "
            f"Error Message: {self.msg}"
        )


class InvalidTypeOrKeywordError(Exception):
    def __init__(self, msg, idx, col, sheet):
        self.msg = msg
        self.idx = idx
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"InvalidTypeOrKeywordError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx}], "
            f"Error Message: {self.msg}"
        )


class CreatNodeError(Exception):
    def __init__(self, msg, idx, node_type, sheet):
        self.msg = msg
        self.idx = idx
        self.node_type = node_type
        self.sheet = sheet

    def __str__(self):
        return (
            f"Failed to create node: "
            f"Node type: [{self.node_type}], "
            f"Sheet: [{self.sheet}]"
            f"Index: [{self.idx}]"
            f"Error Info: {self.msg}"
        )


class GroupRelatedError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"


class ColumnParseError(Exception):
    def __init__(self, message, curr_string):
        self.message = message
        self.curr_string = curr_string

    def __str__(self):
        return f"{self.message} : {self.curr_string}<--"
