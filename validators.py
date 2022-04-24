import configs
import cript as C
from errors import (
    ValueDoesNotExist,
    DuplicatedValueError,
    NullValueError,
    MissingRequiredColumn,
    UnsupportedColumnName,
    InvalidPropertyError,
    InvalidConditionError,
    InvalidQuantityError,
    InvalidIdentifierError,
    InvalidTypeOrKeywordError,
)


def validate_required_cols(sheet_obj):
    """
    Validate that all required columns are present.
    """
    if sheet_obj.df is not None:
        for required_col in sheet_obj.required_cols:
            if required_col not in sheet_obj.cols:
                exception = MissingRequiredColumn(
                    col=required_col,
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
            exception = MissingRequiredColumn(
                col=sheet_obj.either_or_cols,
                sheet=sheet_obj.sheet_name,
                is_either_or_cols=True,
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
                        col=col,
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
                col=from_field,
                sheet=from_sheet_obj.sheet_name,
                sheet_to_check=to_sheet_obj.sheet_name,
                col_to_check=to_field,
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
                            index=index,
                            col=col,
                            sheet=sheet_obj.sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_data_assignment(sheet_obj):
    if sheet_obj.df is not None:
        for parsed_column_name_obj in sheet_obj.parsed_cols.values():
            field_list = parsed_column_name_obj.field_list
            field_type_list = parsed_column_name_obj.field_type_list
            for i in range(2):
                field_type = field_type_list[i]
                nested_field_type = field_type_list[i + 1]
                if field_type is None:
                    continue
                if nested_field_type not in configs.allowed_data_assignment[field_type]:
                    message = (
                        f"[{field_list[i+1]}] cannot be nested to [{field_list[i]}]"
                    )
                    exception = UnsupportedColumnName(
                        col=parsed_column_name_obj.origin_col,
                        sheet=sheet_obj.sheet_name,
                        message=message,
                    )
                    sheet_obj.errors.append(exception.__str__())


def validate_type_or_keyword(sheet_obj):
    if sheet_obj.df is not None:
        for parsed_column_name_obj in sheet_obj.parsed_cols.values():
            field = parsed_column_name_obj.field_list[0]
            field_type = parsed_column_name_obj.field_type_list[0]
            if field == "type" and field_type == "base":
                for index, row in sheet_obj.df.iterrows():
                    sheet_name = sheet_obj.sheet_name
                    col = parsed_column_name_obj.origin_col
                    value = row[col]
                    for supported_type_dict in sheet_obj.param.get(
                        sheet_name + "-type"
                    ):
                        if value == supported_type_dict["name"]:
                            return 0
                    exception = InvalidTypeOrKeywordError(
                        msg=f"{value} is not a supported type",
                        idx=index + 2,
                        col=col,
                        sheet=sheet_name,
                    )
                    sheet_obj.errors.append(exception.__str__())

            if field == "keywords" and field_type == "base":
                for index, row in sheet_obj.df.iterrows():
                    sheet_name = sheet_obj.sheet_name
                    col = parsed_column_name_obj.origin_col
                    value = row[col]
                    value_list = value.split(",")
                    invalid_value_list = []
                    for keyword in value_list:
                        found_tag = False
                        for supported_keyword_dict in sheet_obj.param.get(
                            sheet_name + "-keyword"
                        ):
                            if keyword == supported_keyword_dict["name"]:
                                found_tag = True
                        if not found_tag:
                            invalid_value_list.append(keyword)

                    for invalid_value in invalid_value_list:
                        exception = InvalidTypeOrKeywordError(
                            msg=f"{invalid_value} is not a supported keyword",
                            idx=index + 2,
                            col=col,
                            sheet=sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_property(sheet_obj):
    for key, parsed_object in sheet_obj.parsed.items():
        if type(parsed_object) != type({}):
            continue

        parsed_props = parsed_object.get("prop")
        if parsed_props is not None and len(parsed_props) > 0:
            for prop_key in parsed_props:
                for identifier in parsed_props[prop_key]:
                    parent = parsed_props[prop_key][identifier]
                    try:
                        C.Property(**parent["attr"])
                    except Exception as e_raw:
                        print(parent["attr"])
                        exception = InvalidPropertyError(
                            msg=e_raw.__str__(),
                            idx=parsed_object["index"],
                            col=prop_key,
                            sheet=sheet_obj.sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())

        parsed_conds = parsed_object.get("cond")
        if parsed_conds is not None and len(parsed_conds) > 0:
            for cond_key in parsed_conds:
                for identifier in parsed_conds[cond_key]:
                    parent = parsed_conds[cond_key][identifier]
                    try:
                        C.Condition(**parent["attr"])
                    except Exception as e_raw:
                        exception = InvalidConditionError(
                            msg=e_raw.__str__(),
                            idx=parsed_object["index"],
                            col=cond_key,
                            sheet=sheet_obj.sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_condition(sheet_obj):
    for key, parsed_object in sheet_obj.parsed.items():
        if type(parsed_object) != type({}):
            continue

        parsed_conds = parsed_object.get("cond")
        if parsed_conds is not None and len(parsed_conds) > 0:
            for cond_key in parsed_conds:
                for identifier in parsed_conds[cond_key]:
                    parent = parsed_conds[cond_key][identifier]
                    try:
                        C.Condition(**parent["attr"])
                    except Exception as e_raw:
                        exception = InvalidConditionError(
                            msg=e_raw.__str__(),
                            idx=parsed_object["index"],
                            col=cond_key,
                            sheet=sheet_obj.sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_identity(sheet_obj):
    if sheet_obj.sheet_name != "material":
        return 0

    for key, parsed_object in sheet_obj.parsed.items():
        if type(parsed_object) != type({}):
            continue

        parsed_idens = parsed_object.get("iden")
        if parsed_idens is not None and len(parsed_idens) > 0:
            for iden_key in parsed_idens:
                try:
                    C.Identifier(**parsed_idens[iden_key])
                except Exception as e_raw:
                    exception = InvalidIdentifierError(
                        msg=e_raw.__str__(),
                        idx=parsed_object["index"],
                        col=iden_key,
                        sheet=sheet_obj.sheet_name,
                    )
                    sheet_obj.errors.append(exception.__str__())


def validate_quantity(sheet_obj):
    if sheet_obj.sheet_name != "process ingredient":
        return 0

    for key, parsed_object in sheet_obj.parsed.items():
        if type(parsed_object) != type({}):
            continue

        parsed_quans = parsed_object.get("quan")
        if parsed_quans is not None and len(parsed_quans) > 0:
            for quan_key in parsed_quans:
                try:
                    C.Identifier(**parsed_quans[quan_key])
                except Exception as e_raw:
                    exception = InvalidQuantityError(
                        msg=e_raw.__str__(),
                        idx=parsed_object["index"],
                        col=quan_key,
                        sheet=sheet_obj.sheet_name,
                    )
                    sheet_obj.errors.append(exception.__str__())
