class DataAssignmentError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Data can only be added to a condition or property."


class UnsupportedFieldName(Exception):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return f"'{self.field}' is not a supported field name."


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


class MissingRequiredFieldError(Exception):
    def __init__(self, field, sheet, message=""):
        self.field = field
        self.sheet = sheet
        self.message = message

    def __str__(self):
        return (
            f"'{self.field}' is a required column in the '{self.sheet}' Excel sheet."
            + self.message
        )


class UnsupportedUnitError(Exception):
    def __init__(self, value, field):
        self.value = value
        self.field = field

    def __str__(self):
        return f"'{self.value}' is not a supported unit for '{self.field}'"


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
