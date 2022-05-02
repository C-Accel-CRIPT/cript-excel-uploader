import string
from src.errors import ColumnParseError


class ParsedColumnName:
    """
    parsed_column_name object
    """

    def __init__(
        self,
        is_valid,
        origin_col=None,
        field_list=None,
        identifier=None,
        is_new=None,
    ):
        self.origin_col = origin_col
        self.field_list = field_list
        self.field_type_list = []
        self.identifier = identifier
        self.is_new = is_new
        self.is_valid = is_valid

    def __str__(self):
        return (
            f"origin_col:{self.origin_col}\n"
            f"field_list:{self.field_list}\n"
            f"field_type_list:{self.field_type_list}\n"
            f"identifier:{self.identifier}\n"
            f"is_new_col:{self.is_new}\n"
        )

    def __repr__(self):
        return self.__str__()


def parse_col_name(col):
    """
    parse column name
    (+)--([identifier])--field1(:field2)(field3)
    :param col:
    :return:
    """
    identifier = None
    is_new = False

    p0 = 0
    p1 = 0

    # Check for plus sign and identifier
    tag = False
    for i in range(len(col)):
        if col[i] == "+":
            if i == 0:
                is_new = True
            else:
                raise ColumnParseError("Invalid plus sign", col[: i + 1])
        elif col[i] == "(":
            if identifier is None and not tag:
                tag = True
                p0 = i + 1
            else:
                raise ColumnParseError("Invalid left parenthesis", col[: i + 1])
        elif col[i].isdigit():
            if tag:
                pass
            else:
                raise ColumnParseError(
                    "Numbers are not allowed outside the identifier", col[: i + 1]
                )
        elif col[i] == ")":
            if tag:
                identifier = int(col[p0:i])
                tag = False
            else:
                raise ColumnParseError("Invalid right parenthesis", col[: i + 1])
        elif col[i] in string.punctuation and col[i] not in ["+", "(", ")"]:
            raise ColumnParseError("Invalid punctuation", col[: i + 1])
        elif col[i] == " ":
            raise ColumnParseError("Invalid space", col[: i + 1])
        elif col[i].isalpha():
            if tag:
                raise ColumnParseError(
                    "Characters are not allowed in the identifier", col[: i + 1]
                )
            else:
                p1 = i
                break

    if identifier is None:
        identifier = 1

    # Check for nested fields
    nest_count = 0
    for i in range(p1, len(col)):
        if col[i] == ":":
            nest_count = nest_count + 1
            if nest_count > 2:
                raise ColumnParseError("Too many nested fields", col[: i + 1])
        elif col[i] in string.punctuation and col[i] != "_":
            raise ColumnParseError("Invalid punctuation", col[: i + 1])
        elif col[i] == " ":
            raise ColumnParseError("Invalid space", col[: i + 1])

    field_list = col[p1:].split(":")

    while len(field_list) < 3:
        field_list.append(None)

    return ParsedColumnName(
        is_valid=True,
        origin_col=col,
        field_list=field_list,
        identifier=identifier,
        is_new=is_new,
    )
