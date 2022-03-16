import re

from errors import (
    ValueDoesNotExist,
    DuplicatedValueError,
    NullValueError,
)


def validate_unique_key(sheet_obj):
    # Check for unique keys
    for col in sheet_obj.unique_keys:
        _dict = sheet_obj.unique_keys_dict.get(col)

        if _dict is None or col not in sheet_obj.cols:
            continue

        sheet_obj.unique_keys_dict[col] = {}

        for index, row in sheet_obj.df.iterrows():
            value = row[col]
            if value is None:
                continue
            _value = re.sub(r"[\s]+", "", value).lower()
            if _value in _dict:
                exception = DuplicatedValueError(
                    value1=value,
                    index1=index,
                    value2=sheet_obj.unique_keys_dict[col][_value][0],
                    index2=sheet_obj.unique_keys_dict[col][_value][1],
                    field=col,
                    sheet=sheet_obj.sheet_name,
                )
                sheet_obj.errors.append(exception.__str__())
            else:
                sheet_obj.unique_keys_dict[col].update({_value: [value, index]})


def validate_foreign_key(
    from_field,
    from_sheet_obj,
    to_field,
    to_sheet_obj,
):
    _dict = to_sheet_obj.foreign_keys_dict.get(to_field)
    if (
        _dict is None
        or from_field not in from_sheet_obj.cols
        or to_field not in to_sheet_obj.cols
    ):
        return None

    for index, row in from_sheet_obj.df.iterrows():
        value = row[from_field]
        if value is None:
            continue
        _value = re.sub(r"[\s]+", "", value).lower()
        if _value not in _dict:
            exception = ValueDoesNotExist(
                value=value,
                index=index,
                field=from_field,
                sheet=from_sheet_obj.sheet_name,
                sheet_to_check=to_sheet_obj.sheet_name,
                field_to_check=to_field,
            )
            from_sheet_obj.errors.append(exception.__str__())


def validate_not_null_value(sheet_obj):
    # Check for unique keys
    for col in sheet_obj.not_null_cols:
        if col in sheet_obj.cols:
            for index, row in sheet_obj.df.iterrows():
                value = row[col]
                if value is None or len(str(value).strip()) == 0:
                    exception = NullValueError(
                        index=index, field=col, sheet=sheet_obj.sheet_name
                    )
                    sheet_obj.errors.append(exception.__str__())
