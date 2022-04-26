class UnsupportedColumnName(Exception):
    def __init__(self, col, sheet, field=None, msg=None):
        self.msg = msg
        self.field = field
        self.col = col
        self.sheet = sheet

    def __str__(self):
        if self.msg:
            return (
                f"UnsupportedColumnName: "
                f"Sheet [{self.sheet}], "
                f"Column [{self.col}], "
                f"Input Column name is not supported."
                f"Message: {self.msg}"
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
    def __init__(self, val, col):
        self.val = val
        self.col = col

    def __str__(self):
        return f"'{self.val}' is not a supported value for '{self.col}'"


class ValueDoesNotExist(Exception):
    def __init__(self, val, idx, col, sheet, sheet_to_check, col_to_check):
        self.val = val
        self.idx = idx
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
            f"Index [{self.idx}], "
            f"Value [{self.val}] does not exist "
            f"in the [{self.col_to_check}] column "
            f"of [{self.sheet_to_check}] sheet."
        )


class DuplicatedValueError(Exception):
    def __init__(self, val1, idx1, val2, idx2, col, sheet):
        self.val1 = val1
        self.idx1 = idx1
        self.val2 = val2
        self.idx2 = idx2
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"DuplicatedValueError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx1}], "
            f"Value [{self.val1}] is duplicated with"
            f"value [{self.val2}] at index [{self.idx2}]. "
            f"Each value should be unique in this column."
        )


class NullValueError(Exception):
    def __init__(self, idx, col, sheet):
        self.idx = idx
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"NullValueError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx}], "
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


class InvalidFileSource(Exception):
    def __init__(self, src, idx, col, sheet):
        self.src = src
        self.idx = idx
        self.col = col
        self.sheet = sheet

    def __str__(self):
        return (
            f"InvalidFileSourceError: "
            f"Sheet [{self.sheet}], "
            f"Column [{self.col}], "
            f"Index [{self.idx}], "
            f"Invalid file source: [{self.src}]."
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


class CreatOrUpdateNodeError(Exception):
    def __init__(self, msg, idx, node_type, sheet):
        self.msg = msg
        self.idx = idx
        self.node_type = node_type
        self.sheet = sheet

    def __str__(self):
        return (
            f"Failed to create/update node: "
            f"Node type: [{self.node_type}], "
            f"Sheet: [{self.sheet}], "
            f"Index: [{self.idx}], "
            f"Error Info: {self.msg}"
        )


class ColumnParseError(Exception):
    def __init__(self, msg, curr_string):
        self.msg = msg
        self.curr_string = curr_string

    def __str__(self):
        return f"{self.msg} : {self.curr_string}<--"
