import string
from errors import ColumnParseError


class ParsedColumnName:
    def __init__(self, origin_col, field_list, identifier, is_new_col):
        self.origin_col = origin_col
        self.field_list = field_list
        self.identifier = identifier
        self.is_new_col = is_new_col
        self.field_type_list = []


def parse_col_name(col):
    identifier = None
    is_new_field = False

    p0 = 0
    p1 = 0

    tag = False
    for i in range(len(col)):
        if col[i] == "+":
            if i == 0:
                is_new_field = True
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

    nest_count = 0
    for i in range(p1, len(col)):
        if col[i] == ":":
            nest_count = nest_count + 1
            if nest_count > 2:
                raise ColumnParseError("Too many nested fields", col[: i + 1])
        elif col[i] in string.punctuation:
            raise ColumnParseError("Invalid punctuation", col[: i + 1])
        elif col[i] == " ":
            raise ColumnParseError("Invalid space", col[: i + 1])

    field_list = col[p1:].split(":")

    while len(field_list) < 3:
        field_list.append(None)

    return ParsedColumnName(col, field_list, identifier, is_new_field)
