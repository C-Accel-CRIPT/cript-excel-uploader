import hashlib
import math
import json


def auto_assign_group(group, parent):
    """
    Decide whether to inherit the group from a node's parent.
    e.g., Experiment could inherit the group of it's parent Collection.
    """
    if parent and not group:
        return parent.group
    return group


def sha256_hash(file_path):
    """Generate a SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return str(sha256_hash.hexdigest())


def convert_file_size(size_bytes):
    """Converts file size from bytes to other units."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def display_errors(response):
    """Prep errors sent from API for display."""
    try:
        response_dict = json.loads(response)
    except json.decoder.JSONDecodeError:
        return "Server error."

    if "detail" in response_dict:
        ret = response_dict["detail"]
    elif "errors" in response_dict:
        ret = response_dict["errors"]
    else:
        ret = response_dict

    return json.dumps(ret, indent=4)
