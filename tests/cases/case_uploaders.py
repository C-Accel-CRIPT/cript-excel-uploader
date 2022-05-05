import requests
import cript as C

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
]

"""
test case for get_group(), always false
[group_name, expected_error]
"""
case_get_group_false = [("wrong group", Exception)]

"""
test case for get_collection(), always false
[group_name, expected_error]
"""
case_get_collection_false = [("wrong collection", Exception)]
