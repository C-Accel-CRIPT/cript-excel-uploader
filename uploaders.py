import cript as C
from config import BASE_URL
from errors import GroupRelatedError
from cript.exceptions import DuplicateNodeError
from util import process_track


def connect(token):
    """
    connect with backend service

    :return: backend service connection object
    :rtype: class:`cript.API`
    """
    return C.API(BASE_URL, token)


def get_group(api, group_name):
    """
    search for existing group_url

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_name: group name
    :type group_name: str
    :return: group object
    :rtype: `cript.nodes.Group`
    """
    # Check if Group exists
    my_groups = api.search(C.Group)
    if my_groups["count"] == 0:
        raise GroupRelatedError(
            "Error: You don't belong to any CRIPT group currently. Please contact with us."
        )

    group_search_result = api.search(C.Group, {"name": group_name})
    if group_search_result["count"] == 0 or len(group_name) == 0:
        raise GroupRelatedError(
            "Error: You must enter an existing CRIPT group. Try again."
        )
    else:
        return api.get(group_search_result["results"][0]["url"])


def upload_collection(api, group_obj, coll_name):
    """
    search for existing collection_url, create collection if not exists

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.nodes.Group`
    :param coll_name: collection name
    :type coll_name: str
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: object of collection
    :rtype: `cript.nodes.Group`
    """
    # Check if Collection exists
    try:
        collection_obj = api.get(
            C.Collection,
            {
                "group": group_obj.uid,
                "name": coll_name,
            },
        )
    except DuplicateNodeError:
        collection_obj = None
        print("Error: You must enter an existing CRIPT collection. Try again.")

    return collection_obj


def upload(api, dict, auto_update=False):
    """
    Save objects to database, update them if the object already exists
    """
    count = 0
    for object in dict.values():
        # process-track
        process_track(f"{object.node_name} Uploaded", count, len(dict))

        try:
            api.save(object)
        except DuplicateNodeError:
            url = api.get(object).url
            object.url = url
            api.save(object, auto_update=auto_update)
        except Exception as e:
            print(e.with_traceback)
