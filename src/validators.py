import os
import pandas as pd

from src import configs
import cript as C
from src.errors import (
    ValueDoesNotExist,
    UnsupportedValue,
    DuplicatedValueError,
    NullValueError,
    MissingRequiredColumn,
    UnsupportedColumnName,
    InvalidFileSource,
    InvalidPropertyError,
    InvalidConditionError,
    InvalidQuantityError,
    InvalidIdentifierError,
    InvalidTypeOrKeywordError,
)
from src.util import standardize_name


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
    """
    validate unique keys
    """
    # Check for unique keys
    if sheet_obj.df is not None:
        for col in sheet_obj.unique_keys:
            if col not in sheet_obj.cols:
                continue

            if col not in sheet_obj.unique_keys_dict:
                sheet_obj.unique_keys_dict[col] = {}

            _dict = sheet_obj.unique_keys_dict[col]

            for idx, row in sheet_obj.df.iterrows():
                val = row.get(col)
                if val is None or pd.isna(val):
                    continue
                _val = standardize_name(val)
                if _val in _dict:
                    exception = DuplicatedValueError(
                        val1=val,
                        idx1=idx + 2,
                        val2=sheet_obj.unique_keys_dict[col][_val][0],
                        idx2=sheet_obj.unique_keys_dict[col][_val][1],
                        col=col,
                        sheet=sheet_obj.sheet_name,
                    )
                    sheet_obj.errors.append(exception.__str__())
                else:
                    sheet_obj.unique_keys_dict[col].update({_val: [val, idx + 2]})


def validate_foreign_key(
    from_field,
    from_sheet_obj,
    to_field,
    to_sheet_obj,
):
    """
    Validate foreign keys
    Foreign key pairs to validate are defined in configs.py
    """
    _dict = to_sheet_obj.foreign_keys_dict.get(to_field)
    if (
        _dict is None
        or from_sheet_obj.cols is None
        or to_sheet_obj.cols is None
        or from_field not in from_sheet_obj.cols
        or to_field not in to_sheet_obj.cols
    ):
        return None

    for idx, row in from_sheet_obj.df.iterrows():
        val = row.get(from_field)
        if val is None or pd.isna(val):
            continue
        _val = standardize_name(val)
        if _val not in _dict:
            exception = ValueDoesNotExist(
                val=val,
                idx=idx + 2,
                col=from_field,
                sheet=from_sheet_obj.sheet_name,
                sheet_to_check=to_sheet_obj.sheet_name,
                col_to_check=to_field,
            )
            from_sheet_obj.errors.append(exception.__str__())


def validate_not_null_value(sheet_obj):
    """
    Validate not null value
    Not null cols are defined in configs.py
    """
    # Check for not null value
    if sheet_obj.df is not None:
        for col in sheet_obj.not_null_cols:
            if col in sheet_obj.cols:
                for idx, row in sheet_obj.df.iterrows():
                    val = row.get(col)
                    if val is None or pd.isna(val) or len(str(val).strip()) == 0:
                        exception = NullValueError(
                            idx=idx + 2,
                            col=col,
                            sheet=sheet_obj.sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_file_source(sheet_obj):
    """
    Validate file source in file sheet
    """
    if sheet_obj.sheet_name != "file":
        return 0

    if sheet_obj.df is not None:
        col = "source"
        for idx, row in sheet_obj.df.iterrows():
            val = row.get(col)
            if val is None or not os.path.exists(val):
                exception = InvalidFileSource(
                    src=val,
                    idx=idx + 2,
                    col=col,
                    sheet=sheet_obj.sheet_name,
                )
                sheet_obj.errors.append(exception.__str__())


def validate_field_nesting(sheet_obj):
    """
    Validate field nesting
    """
    if sheet_obj.df is not None:
        for parsed_column_name_obj in sheet_obj.parsed_cols.values():
            if not parsed_column_name_obj.is_valid:
                continue

            field_list = parsed_column_name_obj.field_list
            field_type_list = parsed_column_name_obj.field_type_list

            for i in range(2):
                field_type = field_type_list[i]
                nested_field_type = field_type_list[i + 1]
                if field_type is None:
                    continue
                if nested_field_type not in configs.allowed_field_nesting[field_type]:
                    msg = f"[{field_list[i+1]}] cannot be nested to [{field_list[i]}]"
                    exception = UnsupportedColumnName(
                        msg=msg,
                        col=parsed_column_name_obj.origin_col,
                        sheet=sheet_obj.sheet_name,
                    )
                    sheet_obj.errors.append(exception.__str__())


def validate_type(sheet_obj):
    """
    Validate "type" field
    """
    if sheet_obj.df is not None and sheet_obj.sheet_name in configs.allowed_type:
        param_key = configs.allowed_type.get(sheet_obj.sheet_name)
        for parsed_column_name_obj in sheet_obj.col_parsed.values():
            if not parsed_column_name_obj.is_valid:
                continue

            field = parsed_column_name_obj.field_list[0]
            field_type = parsed_column_name_obj.field_type_list[0]

            if field == "type" and field_type == "base":
                for idx, row in sheet_obj.df.iterrows():
                    sheet_name = sheet_obj.sheet_name
                    col = parsed_column_name_obj.origin_col
                    val = row.get(col)
                    if val is None:
                        continue
                    val = str(val).lower()

                    is_new = False
                    found_tag = False
                    if len(val) > 1 and val[0] == "+":
                        is_new = True
                    for supported_type_dict in sheet_obj.param.get(param_key):
                        if val == supported_type_dict["name"]:
                            found_tag = True
                            break

                    if not found_tag and not is_new:
                        exception = InvalidTypeOrKeywordError(
                            msg=f"{val} is not a supported type",
                            idx=idx + 2,
                            col=col,
                            sheet=sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_keyword(sheet_obj):
    """
    Validate "keyword" or "keywords" field
    """
    if sheet_obj.df is not None and sheet_obj.sheet_name in configs.allowed_keyword:
        param_key = configs.allowed_keyword.get(sheet_obj.sheet_name)
        for parsed_column_name_obj in sheet_obj.col_parsed.values():
            if not parsed_column_name_obj.is_valid:
                continue

            field = parsed_column_name_obj.field_list[0]
            field_type = parsed_column_name_obj.field_type_list[0]

            if field[:7] == "keyword" and field_type == "base":
                for idx, row in sheet_obj.df.iterrows():
                    sheet_name = sheet_obj.sheet_name
                    col = parsed_column_name_obj.origin_col
                    val = row.get(col)
                    if val is None:
                        continue
                    val_list = str(val).lower().split(",")
                    val_list = [val.strip() for val in val_list]
                    invalid_val_list = []
                    for keyword in val_list:
                        is_new = False
                        found_tag = False
                        if len(keyword) > 1 and keyword[0] == "+":
                            is_new = True
                        for supported_keyword_dict in sheet_obj.param.get(param_key):
                            if keyword == supported_keyword_dict["name"]:
                                found_tag = True
                                break

                        if not found_tag and not is_new:
                            invalid_val_list.append(keyword)

                    for invalid_val in invalid_val_list:
                        exception = InvalidTypeOrKeywordError(
                            msg=f"{invalid_val} is not a supported keyword",
                            idx=idx + 2,
                            col=col,
                            sheet=sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())


def validate_property(sheet_obj):
    """
    Validate property fields
    """
    for key, parsed_object in sheet_obj.parsed.items():
        if isinstance(parsed_object, dict):
            _validate_property(sheet_obj, parsed_object)
        elif isinstance(parsed_object, list):
            for parsed_object_nested in parsed_object:
                _validate_property(sheet_obj, parsed_object_nested)


def _validate_property(sheet_obj, parsed_object):
    """
    helper function to validate property fields
    """
    parsed_props = parsed_object.get("prop")
    if parsed_props is not None and len(parsed_props) > 0:
        for prop_key in parsed_props:
            for identifier in parsed_props[prop_key]:
                parent = parsed_props[prop_key][identifier]
                try:
                    C.Property(**parent["attr"])
                except Exception as e_raw:
                    exception = InvalidPropertyError(
                        msg=e_raw.__str__(),
                        idx=parent["idx"],
                        col=parent["col"],
                        sheet=sheet_obj.sheet_name,
                    )
                    sheet_obj.errors.append(exception.__str__())
                finally:
                    # property:condition
                    _validate_condition(sheet_obj, parent)


def validate_condition(sheet_obj):
    """
    Validate condition
    """
    for key, parsed_object in sheet_obj.parsed.items():
        if isinstance(parsed_object, dict):
            _validate_condition(sheet_obj, parsed_object)
        elif isinstance(parsed_object, list):
            for parsed_object_nested in parsed_object:
                _validate_condition(sheet_obj, parsed_object_nested)


def _validate_condition(sheet_obj, parsed_object):
    """
    helper function to validate condition
    """
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
                        idx=parent["idx"],
                        col=parent["col"],
                        sheet=sheet_obj.sheet_name,
                    )
                    sheet_obj.errors.append(exception.__str__())


def validate_identity(sheet_obj):
    """
    Validate identity
    """
    if sheet_obj.sheet_name != "material":
        return 0

    for key, parsed_object in sheet_obj.parsed.items():
        if not isinstance(parsed_object, dict):
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
    """
    Validate quantity
    """
    if sheet_obj.sheet_name != "process ingredient":
        return 0

    for key, parsed_object in sheet_obj.parsed.items():
        if not isinstance(parsed_object, dict):
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


def validate_integer_value(sheet_obj):
    """
    Customized validator for "pages", "year", "volume", "issue" field in citation sheet
    """
    if sheet_obj.sheet_name != "citation":
        return 0
    if sheet_obj.df is not None:
        list_col = "pages"
        single_col = ["year", "volume", "issue", "pmid"]
        for idx, row in sheet_obj.df.iterrows():
            # list value
            list_val = row.get(list_col)
            if list_val is not None:
                val_list = list_val.split(",")
                for _val in val_list:
                    try:
                        int(_val)
                    except Exception:
                        exception = UnsupportedValue(
                            val=_val,
                            idx=idx + 2,
                            col=list_col,
                            sheet=sheet_obj.sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())
            # single value
            for col in single_col:
                single_val = row.get(col)
                if single_val is not None:
                    try:
                        int(single_val)
                    except Exception:
                        exception = UnsupportedValue(
                            val=single_val,
                            idx=idx + 2,
                            col=list_col,
                            sheet=sheet_obj.sheet_name,
                        )
                        sheet_obj.errors.append(exception.__str__())
