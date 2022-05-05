import os
import requests
import cript as C
from src.util import read_config

# Config
dir_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
file_name = "config-test.json"
_config_key_dict, _config_is_found = read_config(dir_path, file_name)
TOKEN = _config_key_dict.get("TOKEN") if "TOKEN" in _config_key_dict else ""

"""
test case for connect(), always false
[base_url, token, expected]
"""
case_connect_false = [
    ("", "", requests.exceptions.MissingSchema),
    ("www.google.com", "", requests.exceptions.MissingSchema),
    (None, None, OSError),
    (None, "Token xxxxxxxx", OSError),
    (
        "https://criptapp-staging.herokuapp.com/",
        "Token xxxxxxxx",
        C.exceptions.APIAuthError,
    ),
    ("https://criptapp-staging.herokuapp.com/", "xxxxxxxx", C.exceptions.APIAuthError),
    ("https://criptapp-staging.herokuapp.com/", None, OSError),
    (
        "https://criptapp-staging.herokuapp.com",
        "Token xxxxxxxx",
        C.exceptions.APIAuthError,
    ),
    ("criptapp-staging.herokuapp.com/", "Token xxxxxxxx", C.exceptions.APIAuthError),
    ("criptapp-staging.herokuapp.com", "Token xxxxxxxx", C.exceptions.APIAuthError),
    ("www.criptapp-staging.herokuapp.com", "Token xxxxxxxx", C.exceptions.APIAuthError),
    (
        "https://criptapp-staging.herokuapp.com/api",
        "Token xxxxxxxx",
        C.exceptions.APIAuthError,
    ),
    (
        "https://criptapp-staging.herokuapp.com/api/",
        "Token xxxxxxxx",
        C.exceptions.APIAuthError,
    ),
    (
        "http://criptapp-staging.herokuapp.com/",
        "Token xxxxxxxx",
        C.exceptions.APIAuthError,
    ),
    (
        "http://criptapp-staging.herokuapp.com/",
        TOKEN.replace("Token", ""),
        C.exceptions.APIAuthError,
    ),
    (
        "http://criptapp-staging.herokuapp.com/",
        TOKEN.replace("Token ", ""),
        C.exceptions.APIAuthError,
    ),
    (
        "http://criptapp-staging.herokuapp.com/",
        TOKEN.replace("Token", "token"),
        C.exceptions.APIAuthError,
    ),
    (
        "http://criptapp-staging.herokuapp.com/",
        TOKEN.replace(" ", ""),
        C.exceptions.APIAuthError,
    ),
    (
        "http://criptapp-staging.herokuapp.com/",
        TOKEN.replace("Token", "Toekn"),
        C.exceptions.APIAuthError,
    ),
]

"""
test case for get_group(), always false
[group_name, expected_error]
"""
case_get_group_false = [
    ("wrong group", Exception),
    (1234, Exception),
    (None, Exception),
    ([1, 2, 3, 4], Exception),
    ({1, 2, 3, 4}, Exception),
    ((1, 2, 3, 4), Exception),
]

"""
test case for get_collection(), always false
[group_name, expected_error]
"""
case_get_collection_false = [
    ("wrong collection", Exception),
    (1234, Exception),
    (None, Exception),
    ([1, 2, 3, 4], Exception),
    ({1, 2, 3, 4}, Exception),
    ((1, 2, 3, 4), Exception),
]
