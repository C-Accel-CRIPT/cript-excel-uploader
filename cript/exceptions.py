"""CRIPT API Errors"""


class APIAuthError(Exception):
    """Raised for errors with API authentication."""

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error


class APIRefreshError(Exception):
    """Raised for errors with refreshing a nodes attribute values."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class APISaveError(Exception):
    """Raised for errors when saving a node to the database."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class APIDeleteError(Exception):
    """Raised for errors when deleting a node to the database."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class APISearchError(Exception):
    """Raised for errors when sending search query."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class APIGetError(Exception):
    """Raised for errors when getting an object from the API."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class APIFileUploadError(Exception):
    """Raised when a file upload fails."""

    def __init__(self):
        pass

    def __str__(self):
        return f"File upload could not be completed."


class APISessionRequiredError(Exception):
    """Raised when an active API session is required but not yet established."""

    def __init__(self):
        pass

    def __str__(self):
        return f"An API session must be established before you can create this node."


class UnsavedNodeError(Exception):
    """Raised when an attempt is made to add an unsaved node to another node."""

    def __init__(self, node_name):
        self.name = node_name

    def __str__(self):
        return (
            f"{self.name} nodes must be saved before they can be added to other nodes."
        )


class AddNodeError(Exception):
    """
    Raised when an attempt is made to add an unrelated node.
    e.g., Attempting to add a Condition node to a Collection node.
    """

    def __init__(self, child_node_name, parent_node_name):
        self.child_node_name = child_node_name
        self.parent_node_name = parent_node_name

    def __str__(self):
        return f"{self.child_node_name} nodes cannot be added to {self.parent_node_name} nodes."


class RemoveNodeError(Exception):
    """
    Raised when an attempt is made to remove an unrelated node.
    e.g., Attempting to remove a Condition node from a Collection node.
    """

    def __init__(self, child_node_name, parent_node_name):
        self.child_node_name = child_node_name
        self.parent_node_name = parent_node_name

    def __str__(self):
        return f"{self.parent_node_name} nodes do not contain {self.child_node_name} nodes."


class InvalidKeyError(Exception):
    """Raised when a key is used that does not exist."""

    def __init__(self, key, category):
        self.key = key
        self.category = category

    def __str__(self):
        return f"'{self.key}' is not a valid {self.category}."


class InvalidValueTypeError(Exception):
    """Raised when a value is an incorrect type."""

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f"{self.key} is using an incorrect value type."


class InvalidValueRangeError(Exception):
    """Raised when a value falls outside the defined range."""

    def __init__(self, key, value, min, max, unit):
        self.key = key
        self.value = value
        self.min = min
        self.max = max
        self.unit = unit

    def __str__(self):
        return (
            f"{self.key} values must be between "
            "{self.min} {self.unit} and {self.max} {self.unit}"
        )


class InvalidUnitError(Exception):
    """Raised when a unit is invalid."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class RequiredUnitError(Exception):
    """Raised when a unit is expected but not provided or vice versa."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class FileSizeLimitError(Exception):
    """Raised when a file size exceeds the defined limit."""

    def __init__(self, max_size):
        self.max_size = max_size

    def __str__(self):
        return f"The file size exceeds the maximum limit of {self.max_size}."
