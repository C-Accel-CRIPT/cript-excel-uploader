def standardize_name(name):
    return name.replace(" ", "").lower()


def filter_required_col(required_col_list):
    new_list = []
    for col_name in required_col_list:
        if col_name not in ["group", "collection", "type"]:
            new_list.append(col_name)

    return new_list
