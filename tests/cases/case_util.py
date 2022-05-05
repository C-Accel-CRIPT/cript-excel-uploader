import os

import pandas as pd
import numpy as np


"""
test case for standardize_name()
[value, expected]
"""
case_standardize_name = [
    ("name", "name"),
    ("", ""),
    (None, None),
    (np.nan, np.nan),
    ("ASD", "asd"),
    ("ORANGE CAT", "orangecat"),
    ("O_r+a*n g#e caT   >  ", "o_r+a*ng#ecat>"),
    ("-*/+-", "-*/+-"),
    (123645, "123645"),
    (123.3450, "123.345"),
    ("123.30000", "123.30000"),
    (-1, "-1"),
    ("你 好", "你好"),
    ("我 是-橘-猫", "我是-橘-猫"),
    ("橘　猪", "橘\u3000猪"),
    ("（）", "（）"),
    ("space         　　　space", "space\u3000\u3000\u3000space"),
    ("Hello sdas", "hellosdas"),
    (" a a a  a  a      a", "aaaaaa"),
    ((1, 2, 3, 4), (1, 2, 3, 4)),
    ({1, 2, 3, 4}, {1, 2, 3, 4}),
]


"""
test case for filter_required_col()
[value, expected]
"""
case_filter_required_col = [
    (["a", "b", "c"], ["a", "b", "c"]),
    (["", "", ""], ["", "", ""]),
    (["a", "b", "group"], ["a", "b"]),
    (["a", "b", "collection"], ["a", "b"]),
    (["a", "b", "type"], ["a", "b"]),
    (["橘猪", "b", "type"], ["橘猪", "b"]),
    (["type"], []),
    ([], []),
]


"""
test case for read_config()
[exe_dir_path, file_name, expected_dict_length, expected_bool]
"""
case_config_dir_path = os.path.join(
    os.path.split(os.path.os.path.realpath(__file__))[0], r"case_util_read_config"
)
case_read_config = [
    (case_config_dir_path, "case_config_1_true.json", 5, True),
    (case_config_dir_path, "case_config_2_true.json", 5, True),
    (case_config_dir_path, "case_config_3_false.json", 0, False),
    (case_config_dir_path, "case_config_4_false.json", 0, False),
    (case_config_dir_path, "case_config_5_true.json", 0, True),
    (case_config_dir_path, "case_config_6_false.json", 0, False),
    (case_config_dir_path, "case_config_7_false.json", 0, False),
    (case_config_dir_path, "case_config_8_false.txt", 0, False),
    (case_config_dir_path, "case_config_not_exist_false.json", 0, False),
]
