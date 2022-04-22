import configs
import cript as C
from transformers import (
    _transform_identifier_list,
    _transform_prop_list,
    _transform_cond_list,
    _transform_quantity_list,
)
from errors import (
    ValueDoesNotExist,
    DuplicatedValueError,
    NullValueError,
    MissingRequiredField,
    UnsupportedUnitName,
    UnsupportedColumnName,
)


def validate_required_cols(sheet_obj):
    """
    Validate that all required columns are present.
    """
    if sheet_obj.df is not None:
        for required_col in sheet_obj.required_cols:
            if required_col not in sheet_obj.cols:
                exception = MissingRequiredField(
                    field=required_col,
                    sheet=sheet_obj.sheet_name,
                    is_either_or_cols=False,
                )
                sheet_obj.errors.append(exception.__str__())


def validate_either_or_cols(sheet_obj):
    """
    Validate that at least one of the either/or columns are present.
    Validation passes when we find one either_or_col name in cols
    """
    if sheet_obj.df is not None:
        exists = False
        if len(sheet_obj.either_or_cols) == 0:
            exists = True

        for either_or_col in sheet_obj.either_or_cols:
            if either_or_col in sheet_obj.cols:
                exists = True
                break

        if not exists:
            exception = MissingRequiredField(
                field=sheet_obj.either_or_cols,
                sheet=sheet_obj.sheet_name,
                is_either_or_cols=True,
            )
            sheet_obj.errors.append(exception.__str__())


def validate_unit(sheet_obj):
    """
    Validate that the input unit is supported
    """
    if sheet_obj.df is not None:
        for col in sheet_obj.cols:
            supported_unit = None
            input_unit = sheet_obj.unit_dict[col]
            if (
                supported_unit is not None
                and input_unit is not None
                and input_unit == supported_unit
            ):
                continue
            elif supported_unit is None and input_unit is None:
                continue
            else:
                exception = UnsupportedUnitName(
                    input_unit=input_unit,
                    supported_unit=supported_unit,
                    field=col,
                    sheet=sheet_obj.sheet_name,
                )
                sheet_obj.errors.append(exception.__str__())


def validate_unique_key(sheet_obj):
    # Check for unique keys
    if sheet_obj.df is not None:
        for col in sheet_obj.unique_keys:
            _dict = sheet_obj.unique_keys_dict.get(col)

            if _dict is None or col not in sheet_obj.cols:
                continue

            sheet_obj.unique_keys_dict[col] = {}

            for index, row in sheet_obj.df.iterrows():
                value = row[col]
                if value is None:
                    continue
                _value = value.replace(" ", "").lower()
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
        _value = value.replace(" ", "").lower()
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
    # Check for not null value
    if sheet_obj.df is not None:
        for col in sheet_obj.not_null_cols:
            if col in sheet_obj.cols:
                for index, row in sheet_obj.df.iterrows():
                    value = row[col]
                    if value is None or len(str(value).strip()) == 0:
                        exception = NullValueError(
                            index=index, field=col, sheet=sheet_obj.sheet_name
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_data_assignment(sheet_obj):
    if sheet_obj.df is not None:
        for parsed_column_name_obj in sheet_obj.parsed_cols.values():
            field_type = parsed_column_name_obj.field_type
            field_nested_type = parsed_column_name_obj.field_nested_type
            if field_nested_type not in configs.allowed_data_assignment[field_type]:
                message = f"[{field_nested_type}] cannot be nested to [{field_type}]"
                exception = UnsupportedColumnName(
                    col=parsed_column_name_obj.origin_col,
                    sheet=sheet_obj.sheet_name,
                    message=message,
                )
                sheet_obj.errors.append(exception.__str__())


# def validate_property(sheet_obj):
#     for parsed in sheet_obj.parsed:
#         parsed_object

# def validate_identity(sheet_obj):
#     for material_std_name in sheet_obj.parsed:
#         parsed_material = sheet_obj.parsed[material_std_name]
#         parsed_idens = parsed_material["iden"]
#         for key in parsed_idens:
#             try:
#                 C.Identifier(parsed_idens[key])
#             except Exception:
#                 sheet_obj.errors.append()
