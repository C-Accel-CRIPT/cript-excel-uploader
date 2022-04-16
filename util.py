from errors import ColumnParseError
import string


def standardize_name(name):
    return name.replace(" ", "").lower()


def process_track(msg, count, total_count):
    count = count + 1
    if count != 0 and count % 10 == 0:
        print(f"{msg}: {count}/{total_count}")


class ParsedColumnName:
    def __init__(self, origin_col, field, field_nested, identifier, is_new_col):
        self.origin_col = origin_col
        self.field = field
        self.field_nested = field_nested
        self.identifier = identifier
        self.is_new_col = is_new_col
        self.field_type = None
        self.field_nested_type = None


def parse_col_name(col):
    field = None
    field_nested = None
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

    col_list = col[p1:].split(":")
    if len(col_list) == 1:
        field = col_list[0]
    elif len(col_list) == 2:
        field = col_list[0]
        field_nested = col_list[1]

    return ParsedColumnName(col, field, field_nested, identifier, is_new_field)
